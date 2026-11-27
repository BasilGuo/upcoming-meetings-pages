#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:      basilguo@163.com
# Date:        2026-11-27 03:26:40
# File Name:   store.py
# Version:     0.0.1
# Description:
import json, pathlib
from datetime import datetime
from .models import Meeting

DATA = pathlib.Path("site/data.json")

def load_existing() -> list[Meeting]:
    if not DATA.exists():
        return []
    try:
        raw = json.loads(DATA.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[WARN] old data.json unreadable: {e}")
        return []
    out = []
    for m in raw.get("meetings", []):
        try:
            out.append(Meeting(
                id=m["id"], name=m["name"], org=m["org"],
                start=m["start"], end=m.get("end") or m["start"],
                location=m.get("location", ""), url=m.get("url", ""),
            ))
        except KeyError:
            continue
    print(f"[INFO] load existing: {len(out)}")
    return out

def merge(old: list[Meeting], new: list[Meeting]) -> list[Meeting]:
    """unique key: org + name + start; old data => new data"""
    bucket: dict[tuple, Meeting] = {}
    for m in old:
        bucket[m.key()] = m
    for m in new:
        bucket[m.key()] = m
    merged = list(bucket.values())
    merged.sort(key=lambda m: (m.start, m.org, m.name))
    return merged

def save(meetings: list[Meeting]) -> None:
    now = datetime.now()
    payload = {
        "generated_at": now.isoformat(timespec="seconds"),
        "count": len(meetings),
        "meetings": [m.to_dict() for m in meetings],
    }
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                    encoding="utf-8")
    print(f"[INFO] save {len(meetings)} meetings -> {DATA}")
