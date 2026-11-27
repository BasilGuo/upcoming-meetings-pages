#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:      basilguo@163.com
# Date:        2026-11-27 03:10:31
# File Name:   models.py
# Version:     0.0.1
# Description:

from dataclasses import dataclass, asdict, field
from datetime import date

@dataclass
class Meeting():
    id: str
    name: str
    org: str
    start: str # YYYY-MM-DD
    end: str   # YYYY-MM-DD
    location: str=""
    url: str=""

    def key(self) -> tuple:
        """unique key: org + name + start"""
        norm = "".join(self.name.lower().split())
        return (self.org.upper(), norm, self.start)

    def to_dict(self) -> dict:
        return asdict(self)
