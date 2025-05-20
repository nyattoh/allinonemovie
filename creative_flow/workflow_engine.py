import os, sys, time, asyncio, yaml
from openai import AsyncOpenAI
from dotenv import load_dotenv, find_dotenv

# ──────────────────────────────────────────
# 環境設定
# ──────────────────────────────────────────
ROOT = os.path.dirname(__file__)
load_dotenv(find_dotenv())
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    sys.exit("❌ OPENAI_API_KEY が設定されていません")
client = AsyncOpenAI(api_key=API_KEY)

# ──────────────────────────────────────────
# YAML 読み込み
# ──────────────────────────────────────────
def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)

graph    = load_yaml(os.path.join(ROOT, "main_workflow.yaml"))
branches = graph.get("branches", {})

# ──────────────────────────────────────────
# ユーザーゲート
# ──────────────────────────────────────────
def user_gate(title: str):
    while True:
        cmd = input(f"[{title}] 次に進みますか？ (y=進む / r=やり直し / q=終了) > ").strip().lower()
        if cmd in ("y", "yes", ""):
            return "next"
        if cmd in ("r", "redo"):
            return "redo"
        if cmd in ("q", "quit"):
            sys.exit("☞ ユーザーが終了を選択しました")

# ──────────────────────────────────────────
# 1. 初期ヒアリング
# ──────────────────────────────────────────
def ask_initial_questions(ctx):
    print("\n=== 初期ヒアリング ===")
    ctx["purpose"] = input("脚本の目的は何ですか？\n> ").strip()
    ctx["character"] = input("主人公の簡潔な説明をしてください。\n> ").strip()
    ctx["setting"] = input("物語の舞台設定を教えてください。\n> ").strip()
    return ctx

def ask_additional_questions(ctx):
    print("\n🔎 情報が不足しています。追加質問 ===")
    ctx["plot_detail"] = input("プロットの要点を詳しく教えてください。\n> ").strip()
    return ctx

def info_sufficient(ctx):
    needed = ["purpose", "character", "setting"]
    return "yes" if all(ctx.get(k) for k in needed) else "no"

# ──────────────────────────────────────────
# 2. 草案プロトタイプ生成
# ──────────────────────────────────────────
async def _call_gpt(prompt: str) -> str:
    resp = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role":"system","content":"あなたは日本語の創作作家です。"},
            {"role":"user","content":prompt}
        ],
        max_tokens=600,
        temperature=0.8
    )
    return resp.choices[0].message.content

def prototype_generation(ctx):
    print("\n=== 草案プロトタイプ生成 (3本) ===")
    base = (
        f"目的: {ctx['purpose']}\n"
        f"主人公: {ctx['character']}\n"
        f"舞台: {ctx['setting']}\n"
        "上記をもとに、短い脚本形式の草案を日本語で3本出力してください。"
    )
    drafts = asyncio.run(asyncio.gather(*[_call_gpt(base) for _ in range(3)]))
    ctx["prototypes"] = drafts
    for i, d in enumerate(drafts, 1):
        print(f"\n--- Prototype {i} ---\n{d}\n")
    return ctx

# ──────────────────────────────────────────
# 3. 草案レビュー
# ──────────────────────────────────────────
def review_drafts(ctx):
    print("\n=== 草案レビュー ===")
    return ctx

def review_result(ctx):
    cmd = input("レビュー結果を選択してください (r=再生成 / y=OK) > ").strip().lower()
    return "redo" if cmd.startswith("r") else "ok"

# ──────────────────────────────────────────
# 4. 分岐：映像化 or 他の工程
# ──────────────────────────────────────────
def next_choice(ctx):
    print("\n=== 次の行き先を選択 ===")
    print("  video: 映像化フローへ")
    print("  other: 他の工程へ")
    print("  continue: 既存プロセス継続")
    cmd = input("選択 > ").strip().lower()
    return cmd if cmd in ("video","other","continue") else "continue"

def video_flow_start(ctx):
    print("\n=== 映像化フロー開始 ===")
    # TODO: I2V/T2V 呼び出し
    return ctx

def other_flow(ctx):
    print("\n=== 他の工程へ進みます ===")
    # TODO: 別工程挿入
    return ctx

# ──────────────────────────────────────────
# 5. 既存 PROCESS1～PROCESS23
# ──────────────────────────────────────────
def _make_process(n):
    def proc(ctx):
        print(f"PROCESS{n}: ダミー処理実行")
        time.sleep(0.1)
        return ctx
    proc.__name__ = f"process_{n}"
    return proc

globals().update({f"process_{i}": _make_process(i) for i in range(1,24)})

# ──────────────────────────────────────────
# 6. フェルミ推定 & 書き直しループ
# ──────────────────────────────────────────
def fermi_evaluate(ctx):
    prob = random.randint(70, 99)
    print(f"読了確率を推定: {prob}%")
    ctx["read_prob"] = prob
    return ctx

def rewrite_needed(ctx):
    return "lt90" if ctx.get("read_prob",0) < 90 else "gte90"

def feedback_analysis(ctx):
    print("フィードバック分析…")
    return ctx

def rewrite_cycle(ctx):
    cnt = ctx.get("rewrite_count",0) + 1
    ctx["rewrite_count"] = cnt
    print(f"書き直しサイクル {cnt} 回目")
    return ctx

# ──────────────────────────────────────────
# エンジン本体
# ──────────────────────────────────────────
def run():
    ctx = {}
    node_id = "START"
    while node_id != "END":
        node = graph["nodes"][node_id]
        # ノード実行
        fn = node.get("func")
        if fn:
            ctx = globals()[fn](ctx)
        # ユーザーゲート
        action = user_gate(node_id)
        if action == "redo":
            continue
        # 分岐 or 次ノード
        if "branch" in node:
            outcome = globals()[node["branch"]](ctx)
            node_id = branches[node["branch"]][outcome]
        else:
            node_id = node.get("next")
    print("\n=== 完了 ===")

if __name__ == "__main__":
    run()
