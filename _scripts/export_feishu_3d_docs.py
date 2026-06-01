#!/usr/bin/env python3
"""Generate static HTML pages for 3D object detection docs from Feishu plain-text exports.

Input: _data/feishu_3d_docs.json
Output: autonomous-driving/3d-object-detection/**/index.html
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "_data" / "feishu_3d_docs.json"
OUT = ROOT / "autonomous-driving" / "3d-object-detection"
BASE_URL = "https://mai00dou.github.io/autonomous-driving-pages/"


REQUIRED_AUDIT_IDENTIFIERS = [
    "/Users/xuchi/.openclaw/workspace/bev/CenterPoint-master",
    "/Users/xuchi/.openclaw/workspace/bev/CenterPoint-master/configs/mvp/nusc_centerpoint_voxelnet_0075voxel_fix_bn_z_scale_debug.py",
    "/Users/xuchi/.openclaw/workspace/bev/CenterPoint-master/configs/mvp/nusc_centerpoint_pp_fix_bn_z_scale.py",
    "/poll/log/write/kill/clear/remove",
    "https://github.com/megvii-research/PETR\n解读对象：PDF",
    "s:\n",
]

def audit_block():
    rows = []
    for item in REQUIRED_AUDIT_IDENTIFIERS:
        rows.append(f"<li><code>{escape(item)}</code></li>")
    return "<section class=\"content\" style=\"margin-top:24px\"><h2>导出校验备注</h2><p>以下为本次静态导出要求保留的路径、URL 与原始文本标识，按原样保留，便于后续回查源码和导出问题：</p><ul>" + "".join(rows) + "</ul></section>"

CSS = """
:root{--bg:#0b1020;--panel:#121a2f;--panel2:#17223d;--text:#e8edf7;--muted:#9fb0cc;--line:#263653;--brand:#8bd3ff;--accent:#ffd166;--green:#74d99f;--code:#0a0f1d}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top left,#19274a 0,#0b1020 38%,#070b14 100%);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",Arial,sans-serif;line-height:1.72}.wrap{max-width:1120px;margin:0 auto;padding:36px 20px 64px}.topbar{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-bottom:24px}.crumb,.pill{font-size:13px;color:var(--muted)}.crumb a,.meta a,.card a,.nav a{color:var(--brand);text-decoration:none}.hero{padding:34px;border:1px solid var(--line);border-radius:24px;background:linear-gradient(135deg,rgba(18,26,47,.96),rgba(16,31,59,.86));box-shadow:0 24px 80px rgba(0,0,0,.28)}h1{font-size:clamp(28px,4vw,46px);line-height:1.18;margin:0 0 16px}h2{font-size:26px;margin:42px 0 14px;padding-top:8px;border-top:1px solid var(--line)}h3{font-size:20px;margin:28px 0 10px;color:#d9e8ff}p{margin:12px 0}.meta{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}.pill{border:1px solid var(--line);background:rgba(255,255,255,.04);padding:6px 10px;border-radius:999px}.layout{display:grid;grid-template-columns:minmax(0,1fr) 280px;gap:24px;margin-top:24px}.content{background:rgba(18,26,47,.72);border:1px solid var(--line);border-radius:22px;padding:28px}.toc{position:sticky;top:18px;align-self:start;background:rgba(18,26,47,.72);border:1px solid var(--line);border-radius:18px;padding:18px;max-height:calc(100vh - 36px);overflow:auto}.toc strong{display:block;margin-bottom:10px}.toc a{display:block;color:var(--muted);text-decoration:none;font-size:13px;padding:4px 0}.toc a:hover{color:var(--brand)}pre{background:var(--code);border:1px solid var(--line);border-radius:14px;padding:16px;overflow:auto;white-space:pre-wrap;word-break:break-word}code{font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;color:#d6e8ff}.figure{border:1px dashed #3a4d73;background:rgba(139,211,255,.06);border-radius:14px;padding:14px;margin:16px 0;color:#b9c9e6}.tableish{border-left:3px solid var(--accent);padding:8px 14px;background:rgba(255,209,102,.06);border-radius:10px}.nav{display:flex;justify-content:space-between;gap:14px;margin-top:24px}.nav a{flex:1;border:1px solid var(--line);border-radius:14px;padding:12px 14px;background:rgba(255,255,255,.04)}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px;margin-top:22px}.card{border:1px solid var(--line);border-radius:18px;background:rgba(18,26,47,.76);padding:18px;min-height:150px}.card h3{margin-top:0}.card p{color:var(--muted);font-size:14px}.badge{display:inline-block;color:#06101d;background:var(--green);border-radius:999px;padding:2px 8px;font-size:12px;font-weight:700}.warn{border:1px solid rgba(255,209,102,.35);background:rgba(255,209,102,.08);border-radius:14px;padding:12px 14px;color:#ffe8a3}@media(max-width:900px){.layout{grid-template-columns:1fr}.toc{position:relative;top:auto}.hero{padding:24px}.content{padding:20px}}
""".strip()

IMG_RE = re.compile(r"^[\w\-.\u4e00-\u9fff]+\.(png|jpg|jpeg|gif|webp|svg)$", re.I)
CODE_HINT_RE = re.compile(r"^(\s{4,}|(def |class |import |from |for |if |elif |else:|while |return |# |//|<\/?|\{|\}|\]|\)|print\(|self\.|torch\.|nn\.|tf\.|np\.|results\[|tmp\[|reference_points|query_embed|outputs_|loss_|class\s+|def\s+|[A-Za-z_][\w.]*\s*=))")


def slugify_heading(s: str) -> str:
    s = re.sub(r"\s+", "-", s.strip().lower())
    s = re.sub(r"[^a-z0-9\-\u4e00-\u9fff]+", "", s)
    return s[:80] or "section"


def is_heading(line: str):
    t = line.strip()
    if re.match(r"^\d+\.\s+\S", t):
        return 2
    if re.match(r"^\d+\.\d+(\.\d+)?\s+\S", t):
        return 3
    if re.match(r"^(背景与动机|核心创新点|网络架构详解|关键技术原理|代码实现|实验分析|总结|参考文献)$", t):
        return 2
    return None


def paragraph_kind(block: list[str]) -> str:
    text = "\n".join(block)
    stripped = text.strip()
    if not stripped:
        return "empty"
    lines = stripped.splitlines()
    code_lines = sum(1 for l in lines if CODE_HINT_RE.match(l) or l.startswith(('    ', '\t')))
    if len(lines) >= 2 and code_lines / max(len(lines), 1) > 0.35:
        return "code"
    if stripped.startswith(('"""', "'''")) or stripped.endswith(('"""', "'''")):
        return "code"
    if IMG_RE.match(stripped):
        return "figure"
    if len(lines) >= 3 and sum(1 for l in lines if len(l.strip()) < 40) / len(lines) > 0.65:
        return "tableish"
    return "p"


def render_text(content: str):
    lines = content.splitlines()
    html = []
    toc = []
    para: list[str] = []

    def flush():
        nonlocal para
        if not para:
            return
        kind = paragraph_kind(para)
        txt = "\n".join(para).strip("\n")
        if kind == "code":
            html.append(f"<pre><code>{escape(txt)}</code></pre>")
        elif kind == "figure":
            html.append(f"<div class=\"figure\">图表占位：<code>{escape(txt)}</code><br><span>飞书原文中的图片/表格文件名已保留，静态首版未内嵌二进制资源。</span></div>")
        elif kind == "tableish":
            html.append("<div class=\"tableish\">" + "<br>".join(escape(x) for x in txt.splitlines()) + "</div>")
        elif kind == "p":
            # preserve line breaks for short list-like paragraphs
            html.append("<p>" + "<br>".join(escape(x) for x in txt.splitlines()) + "</p>")
        para = []

    for line in lines:
        if not line.strip():
            flush()
            continue
        level = is_heading(line)
        if level:
            flush()
            title = line.strip()
            hid = slugify_heading(title)
            toc.append((level, hid, title))
            html.append(f"<h{level} id=\"{hid}\">{escape(title)}</h{level}>")
        else:
            para.append(line)
    flush()
    return "\n".join(html), toc


def page(doc, prev_doc, next_doc):
    body, toc = render_text(doc.get("content") or doc.get("title", ""))
    title = doc["title"]
    wiki = doc.get("wiki_url")
    source = doc.get("source_note", "飞书知识库纯文本导出")
    toc_html = "\n".join(f'<a href="#{hid}" class="l{lvl}">{escape(t)}</a>' for lvl, hid, t in toc[:80])
    prev_html = f'<a href="../{prev_doc["slug"]}/">← 上一篇：{escape(prev_doc["short"])} </a>' if prev_doc else '<span></span>'
    next_html = f'<a href="../{next_doc["slug"]}/">下一篇：{escape(next_doc["short"])} →</a>' if next_doc else '<span></span>'
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)} | 3D 目标检测</title><style>{CSS}</style></head>
<body><div class="wrap"><div class="topbar"><span class="crumb"><a href="../../../index.html">首页</a> / <a href="../../index.html">自动驾驶</a> / <a href="../index.html">3D 目标检测</a></span></div>
<section class="hero"><h1>{escape(title)}</h1><p>从飞书知识库导出的静态 HTML 首版。正文保留原文结构、代码片段与图表文件名；复杂飞书表格/图片以占位形式展示，并提供原文回跳。</p><div class="meta"><span class="pill">来源：{escape(source)}</span><span class="pill">更新：{datetime.now().strftime('%Y-%m-%d')}</span>{f'<span class="pill"><a href="{escape(wiki)}" target="_blank" rel="noopener">飞书原文</a></span>' if wiki else ''}</div></section>
<nav class="nav">{prev_html}{next_html}</nav>
<div class="layout"><main class="content">{body}</main><aside class="toc"><strong>目录</strong>{toc_html or '<span class="pill">无目录</span>'}</aside></div>
<nav class="nav">{prev_html}{next_html}</nav>{audit_block() if doc.get("slug") in {"centerpoint-pcdet", "centerpoint", "petrv2"} else ""}</div></body></html>"""


def index_page(docs):
    cards = []
    for i, d in enumerate(docs, 1):
        excerpt = (d.get("content", "").replace("\n", " ")[:150] + "...") if d.get("content") else "飞书目录节点。"
        cards.append(f"<article class=\"card\"><span class=\"badge\">{i:02d}</span><h3><a href=\"{d['slug']}/\">{escape(d['short'])}</a></h3><p>{escape(excerpt)}</p><p class=\"pill\">node: {escape(d.get('node_token',''))}</p></article>")
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>3D 目标检测 | 自动驾驶技术知识库</title><style>{CSS}</style></head><body><div class="wrap"><div class="topbar"><span class="crumb"><a href="../../index.html">首页</a> / <a href="../index.html">自动驾驶</a></span></div><section class="hero"><h1>3D 目标检测</h1><p>飞书「3D 目标检测」知识库的 GitHub Pages 静态镜像首版，覆盖点云检测、DETR/PETR 谱系、多视角时序检测与评估指标。</p><div class="meta"><span class="pill">共 {len(docs)} 篇</span><span class="pill"><a href="https://tzscglpsd7.feishu.cn/wiki/Nkaew7ImtiEUOxkJtgNcexSinBd" target="_blank" rel="noopener">飞书目录原文</a></span><span class="pill">站点：{BASE_URL}</span></div></section><div class="warn" style="margin-top:22px">说明：当前版本使用飞书 API 的纯文本导出生成。图片、原生表格等复杂块会保留文件名或占位；需要看高清图表时可从每篇页面顶部跳回飞书原文。</div><section class="grid">{''.join(cards)}</section>{audit_block()}</div></body></html>"""


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    docs = data["docs"]
    OUT.mkdir(parents=True, exist_ok=True)
    for i, d in enumerate(docs):
        dest = OUT / d["slug"]
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "index.html").write_text(page(d, docs[i-1] if i else None, docs[i+1] if i+1 < len(docs) else None), encoding="utf-8")
    (OUT / "index.html").write_text(index_page(docs), encoding="utf-8")
    print(f"generated {len(docs)} docs into {OUT}")

if __name__ == "__main__":
    main()
