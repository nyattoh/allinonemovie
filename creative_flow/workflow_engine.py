# workflow_engine.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
workflow_engine.py — AIプロット→草案→レビュー→映像化／他工程→PROCESS1-23→リライト
最小限依存：openai, PyYAML
"""

import os
import sys
import asyncio
import yaml
from openai import AsyncOpenAI

# ─────────────────────────────────────────────────────────────────
# 設定＆クライアント
# ─────────────────────────────────────────────────────────────────
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    sys.exit("❌ 環境変数 OPENAI_API_KEY を設定してください")
client = AsyncOpenAI(api_key=API_KEY)

# ─────────────────────────────────────────────────────────────────
# YAML ロード
# ─────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(__file__)
def load_yaml(fn):
    with open(os.path.join(ROOT, fn), encoding="utf-8") as f:
        return yaml.safe_load(f)

graph    = load_yaml("main_workflow.yaml")
branches = graph["branches"]

# ─────────────────────────────────────────────────────────────────
# ユーザーゲート（各ノード後の操作）
# ─────────────────────────────────────────────────────────────────
def user_gate(title):
    while True:
        cmd = input(f"[{title}] 次に進みますか？ (y=次へ / r=やり直し / q=終了) > ").strip().lower()
        if cmd in ("y", "yes", ""):
            return "next"
        if cmd in ("r", "redo"):
            return "redo"
        if cmd in ("q", "quit"):
            sys.exit("ユーザー終了")

# ─────────────────────────────────────────────────────────────────
# 1. AIによるプロット生成＆選択＋ブラッシュアップ
# ─────────────────────────────────────────────────────────────────
async def _gpt_plot(prompt):
    resp = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role":"system","content":"あなたは創作脚本家です。以下のテーマでプロット案を3つ出してください。"},
            {"role":"user",  "content":prompt}
        ],
        max_tokens=500,
        temperature=0.8
    )
    return resp.choices[0].message.content

def generate_plot_proposals(ctx):
    theme = input("▶ テーマを入力してください：\n> ").strip()
    print("\n=== プロット案を生成中… ===")
    proposals = asyncio.run(asyncio.gather(*[_gpt_plot(theme) for _ in range(3)]))
    ctx["proposals"] = proposals
    for i, p in enumerate(proposals, 1):
        print(f"\n--- Proposal {i} ---\n{p}\n")
    return ctx

def choose_plot(ctx):
    idx = int(input("▶ 採用する案の番号を選んでください (1-3)：\n> ").strip())
    ctx["selected_plot"] = ctx["proposals"][idx-1]
    return "yes"

def refine_plot(ctx):
    print("\n=== プロットブラッシュアップ ===")
    print(ctx["selected_plot"])
    improv = input("変更したい点を入力してください（Enterでスキップ）：\n> ").strip()
    if improv:
        prompt = ctx["selected_plot"] + "\n改善点: " + improv
        improved = asyncio.run(_gpt_plot(prompt))
        ctx["selected_plot"] = improved
        print(f"\n--- 改善後プロット ---\n{improved}\n")
    return ctx

# ─────────────────────────────────────────────────────────────────
# 2. 草案プロトタイプ生成
# ─────────────────────────────────────────────────────────────────
async def _gpt_call(prompt):
    resp = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role":"system","content":"あなたは日本語の創作作家です。"},
            {"role":"user",  "content":prompt}
        ],
        max_tokens=600,
        temperature=0.8
    )
    return resp.choices[0].message.content

def prototype_generation(ctx):
    print("\n=== 草案プロトタイプ(3本) ===")
    base = (
        f"目的: {ctx.get('purpose','')}\n"
        f"主人公: {ctx.get('character','')}\n"
        f"舞台: {ctx.get('setting','')}\n"
        f"プロット: {ctx.get('selected_plot','')}\n"
        "上記をもとに短い脚本形式の草案を3本生成してください。"
    )
    drafts = asyncio.run(asyncio.gather(*[_gpt_call(base) for _ in range(3)]))
    ctx["prototypes"] = drafts
    for i, d in enumerate(drafts, 1):
        print(f"\n--- Draft {i} ---\n{d}\n")
    return ctx

# ─────────────────────────────────────────────────────────────────
# 3. 草案レビュー
# ─────────────────────────────────────────────────────────────────
def review_drafts(ctx):
    print("\n=== 草案レビュー ===")
    return ctx

def review_result(ctx):
    ans = input("再生成しますか？ (r=再生成 / y=OK) > ").strip().lower()
    return "redo" if ans.startswith("r") else "ok"

# ─────────────────────────────────────────────────────────────────
# 4a. 映像化フロー
# ─────────────────────────────────────────────────────────────────
def video_flow_start(ctx):
    print("\n=== 映像化フロー ===")
    return ctx

def other_flow(ctx):
    print("\n=== 他の工程へ ===")
    return ctx

# ─────────────────────────────────────────────────────────────────
# 既存 PROCESS1～PROCESS23／FEEDBACK／REWRITE
# ─────────────────────────────────────────────────────────────────
def process_1(ctx): return ctx
def process_2(ctx): return ctx
def process_3(ctx): return ctx
def process_4(ctx): return ctx
def process_5(ctx): return ctx
def process_6(ctx): return ctx
def process_7(ctx): return ctx
def process_8(ctx): return ctx
def process_9(ctx): return ctx
def process_10(ctx): return ctx
def process_11(ctx): return ctx
def process_12(ctx): return ctx
def process_13(ctx): return ctx
def process_14(ctx): return ctx
def process_15(ctx): return ctx
def process_16(ctx): return ctx
def process_17(ctx): return ctx
def process_18(ctx): return ctx
def process_19(ctx): return ctx
def process_20(ctx): return ctx
def process_21(ctx): return ctx
def process_22(ctx): return ctx
def process_23(ctx): return ctx

def fermi_evaluate(ctx):
    print("=== 読了確率を推定中… ===")
    # 仮実装
    return ctx

def feedback_analysis(ctx):
    print("=== フィードバック分析… ===")
    return ctx

def rewrite_cycle(ctx):
    count = ctx.get("rewrite_count", 0) + 1
    ctx["rewrite_count"] = count
    print(f"=== 書き直しサイクル {count} ===")
    return ctx

# ─────────────────────────────────────────────────────────────────
# エンジン本体
# ─────────────────────────────────────────────────────────────────
def run():
    ctx = {}
    node_id = "START"
    while node_id != "END":
        node = graph["nodes"][node_id]
        if fn := node.get("func"):
            ctx = globals()[fn](ctx)
        act = user_gate(node_id)
        if act == "redo": continue
        if branch := node.get("branch"):
            choice = globals()[branch](ctx)
            node_id = branches[branch][choice]
        else:
            node_id = node.get("next")
    print("\n=== 完了 ===")

if __name__ == "__main__":
    run()
