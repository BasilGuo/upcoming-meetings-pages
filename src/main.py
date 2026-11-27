#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:      basilguo@163.com
# Date:        2026-11-27 03:32:26
# File Name:   main.py
# Version:     0.0.1
# Description:
#!/usr/bin/env python3
"""
Procedure:
1. Load existing meetings
2. Crawl meeting sites
3. Merge meeting events
4. Write down to data.json
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from upcoming_meetings.store import load_existing, merge, save
from upcoming_meetings.spiders import SPIDERS

def main() -> int:
    old = load_existing()

    fresh = []
    with ThreadPoolExecutor(max_workers=len(SPIDERS)) as pool:
        futures = {pool.submit(spider().crawl): spider.__name__ for spider in SPIDERS}
        for fut in as_completed(futures):
            name = futures[fut]
            try:
                fresh.extend(fut.result())
            except Exception as e:
                print(f"[ERROR] {name} failed after retries: {e}")

    if not fresh:
        print("[ERROR] All jobs failed.")
        return 1

    merged = merge(old, fresh)

    save(merged)
    return 0

if __name__ == "__main__":
    sys.exit(main())
