#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:      basilguo@163.com
# Date:        2026-11-27 04:30:51
# File Name:   manrs.py
# Version:     0.0.1
# Description:

import re
import html as htmllib

from ..spider import BaseSpider
from ..models import Meeting

class MANRSSpider(BaseSpider):
    org = "MANRS"
    source_url = "https://manrs.org/resources/events/"
    def parse(self, html: str) -> list[Meeting]:
        pass
