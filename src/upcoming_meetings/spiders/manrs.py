#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:      basilguo@163.com
# Date:        2026-11-27 04:30:51
# File Name:   manrs.py
# Version:     0.0.1
# Description:
import re
import html as htmllib
from datetime import datetime

from ..spider import BaseSpider
from ..models import Meeting

class MANRSSpider(BaseSpider):
    org = "MANRS"
    source_url = "https://manrs.org/resources/events/"

    _LIST = re.compile(
        r'<ul class="card[^"]*">([\s\S]*?)</ul>', re.I)
    _LI = re.compile(r"<li[^>]*>([\s\S]*?)</li>", re.I)
    _TIME = re.compile(r'<time[^>]*datetime="(\d{4}-\d{2}-\d{2})"', re.I)
    _LINK = re.compile(r'<a[^>]*href="([^"]+)"[^>]*>([\s\S]*?)</a>', re.I)
    _PLACE = re.compile(r'<span class="text-sm[^"]*"[^>]*>([\s\S]*?)</span>', re.I)

    def parse(self, html: str) -> list[Meeting]:
        out: list[Meeting] = []
        today = datetime.now().date().isoformat()

        lm = self._LIST.search(html)
        if not lm:
            return out
        for li in self._LI.findall(lm.group(1)):
            tm = self._TIME.search(li)
            if not tm:
                continue
            day = tm.group(1)
            if day < today:
                continue  # only upcoming events

            am = self._LINK.search(li)
            if not am:
                continue
            href, inner = am.group(1), am.group(2)
            slug = href.rstrip("/").rsplit("/", 1)[-1]
            pm = self._PLACE.search(li)
            loc = self.norm_ws(self.strip_tags(pm.group(1))) if pm else ""

            out.append(Meeting(
                id=f"manrs-{slug}", org=self.org,
                name=self.norm_ws(self.strip_tags(inner)),
                start=day, end=day, location=loc, url=href,
            ))

        out.sort(key=lambda x: x.start or "9999")
        return out
