#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:      basilguo@163.com
# Date:        2026-11-27 04:30:29
# File Name:   nanog.py
# Version:     0.0.1
# Description:

import re
import html as htmllib

from ..spider import BaseSpider
from ..models import Meeting

class NANOGSpider(BaseSpider):
    org = "NANOG"
    source_url = "https://nanog.org/events/future/?type=conference"
    def parse(self, html: str) -> list[Meeting]:
        pass
