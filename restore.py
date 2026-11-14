# -*- coding: utf-8 -*-
"""按 MANIFEST.json 合并三个仓库中的分片并校验 SHA256。
用法: python restore.py [输出目录]
"""
import os
import sys
import json
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, "restored")

with open(os.path.join(HERE, "MANIFEST.json"), encoding="utf-8") as f:
    man = json.load(f)

os.makedirs(OUT, exist_ok=True)
for ent in man["files"]:
    dst = os.path.join(OUT, ent["name"])
    whole = hashlib.sha256()
    with open(dst, "wb") as o:
        for p in ent["parts"]:
            src = os.path.join(ROOT, p["repo"], man["subdir"], p["file"])
            if not os.path.isfile(src):
                raise SystemExit("缺少分片: %s" % src)
            with open(src, "rb") as f:
                buf = f.read()
            if len(buf) != p["size"] or hashlib.sha256(buf).hexdigest() != p["sha256"]:
                raise SystemExit("分片校验失败: %s" % src)
            whole.update(buf)
            o.write(buf)
    ok_size = os.path.getsize(dst) == ent["size"]
    ok_hash = whole.hexdigest() == ent["sha256"]
    print("%s  size=%s  sha256=%s" % (ent["name"], "OK" if ok_size else "FAIL", "OK" if ok_hash else "FAIL"))
    if not (ok_size and ok_hash):
        raise SystemExit("还原失败: %s" % ent["name"])
print("全部还原完成 ->", OUT)
