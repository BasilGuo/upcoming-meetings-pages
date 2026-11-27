#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:      basilguo@163.com
# Date:        2026-11-27 04:10:22
# File Name:   ietf.py
# Version:     0.0.1
# Description:
import re
import html as htmllib

from ..spider import BaseSpider
from ..models import Meeting

class IETFSpider(BaseSpider):
    org = "IETF"
    source_url = "https://www.ietf.org/meeting/upcoming/"

    _BLOCK = re.compile(r"<h2[^>]*>([\s\S]*?)</h2>\s*<p[^>]*>([\s\S]*?)</p>", re.I)
    _TITLE = re.compile(r"IETF\s+(\d+)", re.I)
    _LINK = re.compile(r'<a[^>]*href="([^"]+)"', re.I)
    _BOLD = re.compile(r"<(b|i)>([^<]+)</\1>", re.I)

    def parse(self, html: str) -> list[Meeting]:
        out: list[Meeting] = []
        seen: set[str] = set()

        for h2_inner, p_inner in self._BLOCK.findall(html):
            tm = self._TITLE.search(self.strip_tags(h2_inner))
            if not tm:
                continue
            num = tm.group(1)
            if num in seen:
                continue

            lm = self._LINK.search(h2_inner)
            if lm:
                link = lm.group(1)
                if link.startswith("/"):
                    link = "https://www.ietf.org" + link
            else:
                link = f"https://www.ietf.org/meeting/{num}/"

            p_text = self.norm_ws(self.strip_tags(p_inner))
            dr = self.parse_date_range(p_text)
            if not dr:
                continue
            start, end = dr

            bm = self._BOLD.search(p_inner)
            if bm:
                location = self.norm_ws(bm.group(2))
            else:
                m = self._DATE_RANGE.search(p_text)
                location = p_text[m.end():].lstrip(". ").strip() if m else ""

            out.append(Meeting(
                id=f"ietf-{num}", name=f"IETF {num}", org=self.org,
                start=start, end=end, location=location[:120], url=link,
            ))
            seen.add(num)

        out.sort(key=lambda x: x.start or "9999")
        return out
