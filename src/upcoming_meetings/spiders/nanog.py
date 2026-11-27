#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:      basilguo@163.com
# Date:        2026-11-27 04:30:29
# File Name:   nanog.py
# Version:     0.0.1
# Description:
import re
import html as htmllib
import urllib.error

from ..spider import BaseSpider
from ..models import Meeting

class NANOGSpider(BaseSpider):
    org = "NANOG"
    source_url = "https://nanog.org/events/future/?type=conference"

    _TABLE = re.compile(
        r'role="table"[^>]*aria-label="Destinations"([\s\S]*?)</div>\s*</div>', re.I)
    _ROW = re.compile(r'<div[^>]*role="rowgroup"[^>]*>([\s\S]*?)</div>', re.I)
    _NAME = re.compile(r"NANOG\s+(\d+)", re.I)
    _DATE = re.compile(
        r"([A-Za-z]{3,9})\s+(\d{1,2}),\s*(\d{4})\s*[-\u2013]\s*"
        r"([A-Za-z]{3,9})\s+(\d{1,2}),\s*(\d{4})", re.I)
    _GAP = re.compile(
        r"</p>\s*([\s\S]*?)\s*<p[^>]*>[A-Za-z]{3,9}\s+\d{1,2},\s*\d{4}", re.I)
    _BR = re.compile(r"<br\s*/?>", re.I)

    def fetch_html(self) -> str:
        # nanog.org is served behind a Cloudflare firewall.  From some
        # networks every request, including the homepage, is answered with
        # HTTP 403 "Attention Required" - an IP-level block that this
        # crawler cannot bypass.  Instead of retrying and failing the whole
        # run, log it and fall back to an empty page so no meetings are
        # reported this time.  The parser still runs on the live page when
        # the site is reachable again (e.g. from GitHub Actions).
        try:
            return super().fetch_html()
        except urllib.error.HTTPError as e:
            print(f"[INFO] {self.org}: {self.source_url} blocked by remote "
                  f"(HTTP {e.code} {e.reason}); skipping")
        except OSError as e:
            # URLError, connection reset, DNS failure, timeout, ...
            print(f"[INFO] {self.org}: {self.source_url} unreachable ({e}); skipping")
        return "<html></html>"

    def parse(self, html: str) -> list[Meeting]:
        out: list[Meeting] = []
        seen: set[str] = set()

        tm = self._TABLE.search(html)
        if not tm:
            return out
        for row in self._ROW.findall(tm.group(1)):
            nm = self._NAME.search(self.strip_tags(row))
            if not nm:
                continue
            num = nm.group(1)
            if num in seen:
                continue

            dm = self._DATE.search(row)
            if not dm:
                continue
            mon1, d1, y1, mon2, d2, y2 = dm.groups()
            m1 = self.MONTHS_ABBR.get(mon1[:3].lower())
            m2 = self.MONTHS_ABBR.get(mon2[:3].lower())
            if not m1 or not m2:
                continue
            start = f"{y1}-{m1:02d}-{int(d1):02d}"
            end = f"{y2}-{m2:02d}-{int(d2):02d}"

            photo = self._GAP.search(row) if self._GAP.search(row) else None
            loc = ""
            if photo:
                lines = [self.norm_ws(x) for x in self._BR.split(photo.group(1))]
                lines = [x for x in lines if x]
                if lines:
                    loc = lines[-1]

            out.append(Meeting(
                id=f"nanog-{num}", name=f"NANOG {num}", org=self.org,
                start=start, end=end, location=loc,
                url=f"https://nanog.org/events/nanog-{num}/",
            ))
            seen.add(num)

        out.sort(key=lambda x: x.start or "9999")
        return out
