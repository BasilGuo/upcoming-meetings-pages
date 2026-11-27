#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:      basilguo@163.com
# Date:        2026-11-27 03:14:04
# File Name:   spider.py
# Version:     0.0.1
# Description:

from abc import ABC, abstractmethod
from .models import Meeting
import time, functools
import re
import html as htmllib

def retry(times: int=3, delay: float=2.0, backoff: float=2.0):
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*a, **kw):
            last = None
            wait = delay
            for i in range(1, times+1):
                try:
                    return fn(*a, **kw)
                except Exception as e:
                    last = e
                    print(f"[INFO] [retry {i}/{times}] {fn.__qualname__}: {e}")
                    if i < times:
                        time.sleep(wait)
                        wait *= backoff
            raise last
        return wrapper
    return deco

class BaseSpider(ABC):
    org: str = ""
    source_url: str = ""

    MONTHS = {m: i for i, m in enumerate(
        ["January", "February", "March", "April", "May", "June",
         "July", "August", "September", "October", "November", "December"], 1)}
    MONTHS_ABBR = {m[:3].lower(): i for m, i in MONTHS.items()}
    _TAG = re.compile(r"<[^>]+>")
    _ISO = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
    _DATE_RANGE = re.compile(
        r"([A-Za-z]+)\s+(\d{1,2})"
        r"(?:\s*-\s*(?:([A-Za-z]+)\s+)?(\d{1,2}))?"
        r",?\s*(\d{4})"
    )

    _HEADERS = {
        "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/131.0.0.0 Safari/537.36"),
        "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
                   "image/avif,image/webp,*/*;q=0.8"),
        "Accept-Language": "en-US,en;q=0.9",
    }

    @classmethod
    def strip_tags(cls, s: str) -> str:
        return htmllib.unescape(cls._TAG.sub(" ", s)).replace("\xa0", " ")

    @staticmethod
    def norm_ws(s: str) -> str:
        return re.sub(r"\s+", " ", s).strip()

    @classmethod
    def parse_date_range(cls, text: str):
        # ISO date format: 2027-03-06
        m = cls._ISO.search(text)
        if m:
            s = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
            return s, s

        # March 6-12, 2027' / 'March 26-April 1, 2033' -> ('YYYY-MM-DD','YYYY-MM-DD')
        m = cls._DATE_RANGE.search(text)
        if not m:
            return None
        mon1, d1, mon2, d2, year = (
            m.group(1), int(m.group(2)), m.group(3), m.group(4), int(m.group(5)))
        m1 = cls.MONTHS.get(mon1) or cls.MONTHS_ABBR.get(mon1[:3].lower())
        if not m1:
            return None
        start = f"{year}-{m1:02d}-{d1:02d}"
        em, ed = m1, d1
        if d2:
            ed = int(d2)
            if mon2:
                em = cls.MONTHS.get(mon2) or cls.MONTHS_ABBR.get(mon2[:3].lower())
                if not em:
                    return None
        return start, f"{year}-{em:02d}-{ed:02d}"

    @abstractmethod
    def parse(self, html: str) -> list[Meeting]:
        ...

    def fetch_html(self) -> str:
        import urllib.request
        req = urllib.request.Request(
            self.source_url,
            headers=self._HEADERS,
        )
        with urllib.request.urlopen(req, timeout=25) as r:
            charset = r.headers.get_content_charset() or "utf-8"
            return r.read().decode(charset, errors="replace")

    @retry(times=3, delay=2.0)
    def crawl(self) -> list[Meeting]:
        html = self.fetch_html()
        if not html.strip():
            raise ValueError(f"{self.org}: empty response")
        items = self.parse(html)
        for m in items:
            m.org = self.org
            if not m.url:
                m.url = self.source_url
        print(f"[INFO] crawled {self.org}: {len(items)} meetings")
        return items
