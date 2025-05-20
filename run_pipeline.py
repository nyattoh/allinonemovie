#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_pipeline.py — YAML Only Video-Orchestrator  v0.4  (OpenAI v1.x 対応)
  * !include 展開
  * 最新 AI プロンプト Tips 取得 & 24h キャッシュ
  * GPT-4o で 10 ペルソナ並列ドラフト生成 (AsyncOpenAI)
  * スコアリング → 上位 3 本を drafts_yyyymmdd_HHMMSS に保存
"""

import os, sys, time, asyncio, pathlib, requests, yaml
from bs4 import BeautifulSoup
from openai import AsyncOpenAI           # ★ v1.x クライアント
from dotenv import load_dotenv, find_dotenv

ROOT  = pathlib.Path(__file__).parent
CACHE = ROOT / "includes" / "ai_prompt_tips"

# ────────────────────────────────────────────────────────────
# 0) 環境変数
# ────────────────────────────────────────────────────────────
load_dotenv(find_dotenv())
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    sys.exit("❌  OPENAI_API_KEY が見つかりません .env を確認してください")
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# ────────────────────────────────────────────────────────────
# 1) !include 対応 YAML ローダー
# ────────────────────────────────────────────────────────────
def load_yaml(path: pathlib.Path):
    """!include を再帰展開して dict にして返す"""
    def _include(loader, node):
        inc_path = ROOT / node.value
        with open(inc_path, "r", encoding="utf-8") as f:
            return yaml.load(f, Loader=yaml.SafeLoader)
    yaml.SafeLoader.add_constructor("!include", _include)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.load(f, Loader=yaml.SafeLoader)

# ────────────────────────────────────────────────────────────
# 2) プロンプト Tips 取得 (DuckDuckGo) & キャッシュ
# ────────────────────────────────────────────────────────────
def fetch_prompt_tips(model_name: str) -> pathlib.Path:
    CACHE.mkdir(exist_ok=True)
    cache_file = CACHE / f"{model_name}.yaml"
    if cache_file.exists() and time.time() - cache_file.stat().st_mtime < 86_400:
        return cache_file

    query = f"{model_name} best prompt parameters"
    print(f"[Fetch] {query}")
    html = requests.get(f"https://duckduckgo.com/html/?q={query}", timeout=30).text
    soup = BeautifulSoup(html, "html.parser")
    tips = [a.text.strip() for a in soup.select(".result__snippet")[:5]]
    yaml.safe_dump({"tips": tips}, cache_file.open("w", encoding="utf-8"), allow_unicode=True)
    return cache_file

# ────────────────────────────────────────────────────────────
# 3) OpenAI 非同期 Persona 生成（GPT-4o）
# ────────────────────────────────────────────────────────────
async def _gen_single(idx: int, prompt: str, system_msg: str):
    resp = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": prompt}
        ],
        max_tokens=600,
        temperature=0.9,
    )
    return {
        "id": idx,
        "text": resp.choices[0].message.content,
        "scores": {"coherence": 0, "creativity": 0, "pacing": 0}
    }

def generate_persona_writings(count: int, prompt: str):
    """GPT-4o を並列 10 本（count）呼び出してドラフトを返す"""
    system_msg = "You are a skilled novelist. Write a vivid draft based on the prompt."
    async def _run():
        tasks = [_gen_single(i + 1, prompt, system_msg) for i in range(count)]
        return await asyncio.gather(*tasks)
    return asyncio.run(_run())

# ────────────────────────────────────────────────────────────
# 4) スコアリング（ダミー合計点）
# ────────────────────────────────────────────────────────────
def top_k_writings(writings, k):
    def total(w): return sum(w["scores"].values())
    return sorted(writings, key=total, reverse=True)[:k]

# ────────────────────────────────────────────────────────────
# 5) メイン
# ────────────────────────────────────────────────────────────
def main(yaml_path: str):
    cfg = load_yaml(ROOT / yaml_path)

    # 例：Runway Gen-2 の最新 Tips を取得
    tips_path = fetch_prompt_tips("Runway Gen-2")
    print(f"[Tips Cached] {tips_path.relative_to(ROOT)}")

    # ------------- Persona Draft Pipeline -------------
    wp      = cfg["writing_pipeline"]
    count   = wp["persona_generator"]["count"]       # 10
    prompt  = "Generate an opening scene about a black-cat detective."
    writings = generate_persona_writings(count, prompt)
    best     = top_k_writings(writings, wp["scoring"]["top_k"])  # top 3

    # ------------- ファイル出力 -------------
    out_dir = ROOT / f"{wp['output']['folder_prefix']}{time.strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(exist_ok=True)
    for w in best:
        fn = wp["output"]["filename_pattern"].replace("{{id}}", str(w["id"]))
        (out_dir / fn).write_text(w["text"], encoding="utf-8")
    print(f"[Done] top {len(best)} drafts saved to {out_dir}")

# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    default = "main.yml" if (ROOT / "main.yml").exists() else "main.yaml"
    main(sys.argv[1] if len(sys.argv) > 1 else default)
