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
    def parse(self, html: str) -> list[Meeting]:
        pass
