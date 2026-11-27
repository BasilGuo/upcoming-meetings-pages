#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:      basilguo@163.com
# Date:        2026-11-27 04:28:37
# File Name:   ripe.py
# Version:     0.0.1
# Description:
import re
import html as htmllib

from ..spider import BaseSpider
from ..models import Meeting

class RIPESpider(BaseSpider):
    org = "RIPE"
    source_url = "https://www.ripe.net/meetings/ripe-meetings/upcoming-ripe-meetings/"

    _ITEM = re.compile(
        r'<div class="grid grid-flow-row md:grid-cols-3[^"]*">([\s\S]*?)</div>', re.I)
    _LINK = re.compile(r'<a[^>]*href="([^"]+)"[^>]*>([\s\S]*?)</a>', re.I)
    _TIME = re.compile(r'<time[^>]*datetime="(\d{4}-\d{2}-\d{2})"', re.I)
    _PLACE = re.compile(r'<span class="text-start[^"]*"[^>]*>([\s\S]*?)</span>', re.I)
    _NUM = re.compile(r"RIPE\s*(\d+)", re.I)

    def parse(self, html: str) -> list[Meeting]:
        out: list[Meeting] = []
        seen: set[str] = set()

        for item in self._ITEM.findall(html):
            lm = self._LINK.search(item)
            if not lm:
                continue
            href, inner = lm.group(1), lm.group(2)
            nm = self._NUM.search(self.norm_ws(self.strip_tags(inner)))
            if not nm:
                continue
            num = nm.group(1)
            if num in seen:
                continue

            times = self._TIME.findall(item)
            if len(times) < 2:
                continue
            start, end = times[0], times[1]

            pm = self._PLACE.search(item)
            loc = self.norm_ws(self.strip_tags(pm.group(1))) if pm else ""
            link = href if href.startswith("http") else "https://www.ripe.net" + href

            out.append(Meeting(
                id=f"ripe-{num}", name=f"RIPE {num}", org=self.org,
                start=start, end=end, location=loc, url=link,
            ))
            seen.add(num)

        out.sort(key=lambda x: x.start or "9999")
        return out
