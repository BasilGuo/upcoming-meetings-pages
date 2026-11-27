#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:      basilguo@163.com
# Date:        2026-11-27 04:27:11
# File Name:   apnic.py
# Version:     0.0.1
# Description:
import re
import html as htmllib
from datetime import datetime

from ..spider import BaseSpider
from ..models import Meeting

class APNICSpider(BaseSpider):
    org = "APNIC"
    source_url = "https://www.apnic.net/events/conferences/"

    _TABLE = re.compile(r'<table class="table">([\s\S]*?)</table>', re.I)
    _TR = re.compile(r"<tr[^>]*>([\s\S]*?)</tr>", re.I)
    _TD = re.compile(r"<td[^>]*>([\s\S]*?)</td>", re.I)
    _BR = re.compile(r"<br\s*/?>", re.I)
    # '4 - 12 February' / '2 - 9 September' (single month, day range)
    _ONE_MONTH = re.compile(
        r"(\d{1,2})\s*[-\u2013]\s*(\d{1,2})\s+([A-Za-z]+)")
    # '24 February - 4 March' (two months, one day range)
    _TWO_MONTH = re.compile(
        r"(\d{1,2})\s+([A-Za-z]+)\s*[-\u2013]\s*(\d{1,2})\s+([A-Za-z]+)")
    _NUM_BASE = 60  # APNIC 61 (2026) was the first scheduled conference

    def _date(self, text: str, year: int):
        # Normalise 'd - d month' / 'd month - d month' into the
        # 'month d - d, year' form that BaseSpider.parse_date_range expects.
        m = self._TWO_MONTH.search(text)
        if m:
            d1, mon1, d2, mon2 = m.groups()
            norm = f"{mon1} {d1}-{mon2} {d2}, {year}"
        else:
            m = self._ONE_MONTH.search(text)
            if not m:
                return None
            d1, d2, mon = m.groups()
            norm = f"{mon} {d1}-{d2}, {year}"
        return self.parse_date_range(norm)

    def parse(self, html: str) -> list[Meeting]:
        out: list[Meeting] = []
        seen: set[str] = set()
        today = datetime.now().date().isoformat()

        tm = self._TABLE.search(html)
        if not tm:
            return out

        used = self._NUM_BASE
        for tr in self._TR.findall(tm.group(1)):
            cells = self._TD.findall(tr)
            if len(cells) < 3:
                continue
            year_str = self.norm_ws(self.strip_tags(cells[0]))
            if not year_str.isdigit():
                continue
            year = int(year_str)

            # column order in each row: APRICOT, APNIC
            for col, td in enumerate(cells[1:3]):
                lines = [self.norm_ws(self.strip_tags(x)) for x in self._BR.split(td)]
                lines = [x for x in lines if x]
                if not lines or lines[-1].lower() == "tbc":
                    continue

                dr = self._date(" ".join(lines[1:]), year)
                if not dr:
                    continue
                used += 1
                start, end = dr
                if end < today:
                    continue  # keep numbering, drop past conferences
                num = used

                if col == 0:
                    name = f"APNIC {num} - APRICOT {year}"
                    mid = f"apnic-{num}-apricot-{year}"
                else:
                    name = f"APNIC {num}"
                    mid = f"apnic-{num}"
                if mid in seen:
                    continue

                out.append(Meeting(
                    id=mid, name=name, org=self.org,
                    start=start, end=end, location=lines[0][:120],
                    url=f"https://www.apnic.net/events/conferences/{mid}/",
                ))
                seen.add(mid)

        out.sort(key=lambda x: x.start or "9999")
        return out
