#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:      basilguo@163.com
# Date:        2026-11-27 04:27:11
# File Name:   apnic.py
# Version:     0.0.1
# Description:

import re
import html as htmllib

from ..spider import BaseSpider
from ..models import Meeting

class APNICSpider(BaseSpider):
    org = "APNIC"
    source_url = "https://www.apnic.net/events/conferences/"
    def parse(self, html: str) -> list[Meeting]:
        pass
