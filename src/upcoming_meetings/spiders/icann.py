#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:      basilguo@163.com
# Date:        2026-11-27 04:30:01
# File Name:   icann.py
# Version:     0.0.1
# Description:
import re
import html as htmllib
from datetime import datetime

from ..spider import BaseSpider
from ..models import Meeting

class ICANNspider(BaseSpider):
    org = "ICANN"
    source_url = "https://meetings.icann.org/en/calendar"

    _TR = re.compile(r"<tr[^>]*>([\s\S]*?)</tr>", re.I)
    _TD = re.compile(r"<td[^>]*>([\s\S]*?)</td>", re.I)
    # '30 Oct - 4 Nov 2027' / '28 February-4 March 2032'
    _TWO_MONTH = re.compile(
        r"(\d{1,2})\s*[-\u2013]\s*([A-Za-z]{3,9})\s*[-\u2013]\s*(\d{1,2})\s+([A-Za-z]{3,9}),?\s+(\d{4})")
    # '22-29 October 2033' / '6-9 June 2033'
    _ONE_MONTH = re.compile(
        r"(\d{1,2})\s*[-\u2013]\s*(\d{1,2})\s+([A-Za-z]{3,9}),?\s+(\d{4})")

    def _date(self, dates: str):
        m = self._TWO_MONTH.search(dates)
        if m:
            d1, mon1, d2, mon2, year = m.groups()
            m2 = self.MONTHS.get(mon2) or self.MONTHS_ABBR.get(mon2[:3].lower())
            if not m2:
                return None
        else:
            m = self._ONE_MONTH.search(dates)
            if not m:
                return None
            d1, d2, mon1, year = m.groups()
            m2 = None
        m1 = self.MONTHS.get(mon1) or self.MONTHS_ABBR.get(mon1[:3].lower())
        if not m1:
            return None
        year = int(year)
        start = f"{year}-{m1:02d}-{int(d1):02d}"
        em, ed = m1 if not m2 else m2, int(d2)
        return start, f"{year}-{em:02d}-{ed:02d}"

    def parse(self, html: str) -> list[Meeting]:
        out: list[Meeting] = []
        seen: set[str] = set()
        today = datetime.now().date().isoformat()

        for tr in self._TR.findall(html):
            tds = self._TD.findall(tr)
            if len(tds) < 4:
                continue
            name = self.norm_ws(self.strip_tags(tds[0]))
            mtype = self.norm_ws(self.strip_tags(tds[1]))
            dates = self.norm_ws(self.strip_tags(tds[2]))
            loc = self.norm_ws(self.strip_tags(tds[3]))
            if not name or not dates:
                continue

            dr = self._date(dates)
            if not dr:
                continue
            start, end = dr
            if end < today:
                continue  # only upcoming meetings

            mid = f"icann{name.lower()}"
            if mid in seen:
                continue
            nname = f"{name} ({mtype})" if mtype else name
            out.append(Meeting(
                id=mid, name=nname, org=self.org,
                start=start, end=end, location=loc[:120],
                url=f"https://meetings.icann.org/en/meetings/{name.lower()}",
            ))
            seen.add(mid)

        out.sort(key=lambda x: x.start or "9999")
        return out
