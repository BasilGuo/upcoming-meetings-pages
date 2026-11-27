#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:      basilguo@163.com
# Date:        2026-11-27 04:30:01
# File Name:   icann.py
# Version:     0.0.1
# Description:

import re
import html as htmllib

from ..spider import BaseSpider
from ..models import Meeting

class ICANNspider(BaseSpider):
    org = "ICANN"
    source_url = "https://meetings.icann.org/en/calendar"
    def parse(self, html: str) -> list[Meeting]:
        pass
