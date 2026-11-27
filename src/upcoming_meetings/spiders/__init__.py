#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:      basilguo@163.com
# Date:        2026-11-27 04:10:01
# File Name:   __init__.py
# Version:     0.0.1
# Description:
from .ietf import IETFSpider
from .apnic import APNICSpider
from .ripe import RIPESpider
from .icann import ICANNspider
from .nanog import NANOGSpider
from .manrs import MANRSSpider

SPIDERS = [IETFSpider, APNICSpider, RIPESpider, ICANNspider, NANOGSpider, MANRSSpider]
