
import yaml, asyncio, os, sys, time, random
from openai import AsyncOpenAI
from dotenv import load_dotenv, find_dotenv

ROOT = os.path.dirname(__file__)
load_dotenv(find_dotenv())
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)

graph = load_yaml(os.path.join(ROOT, "main_workflow.yaml"))
branches = graph["branches"]

# ---------- Node Function Stubs ----------
def ask_initial_questions(ctx):
    qs = load_yaml(os.path.join(ROOT, "user_prompt_questions.yaml"))
    print("\n=== 初期ヒアリング ===")
    for q in qs:
        txt = q["question_jp"]
        var = q["variable"].strip("{} ")
        default = q.get("default","")
        ans = input(f"{txt}\n> ").strip() or default
        ctx[var] = ans
    # 追加質問
    need = input("プロットのブラッシュアップを行いますか？ (y/N) > ").strip().lower()
    ctx["plot_refine"] = need.startswith("y")
    return ctx

def plot_refine_needed(ctx):
    return "yes" if ctx.get("plot_refine") else "no"

async def refine_dialog(ctx, prompt):
    resp = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role":"system","content":"あなたは優秀な編集者です。"},
            {"role":"user","content":prompt}
        ],
        max_tokens=300, temperature=0.7)
    print("\n--- ブラッシュアップ案 ---\n",resp.choices[0].message.content)
    input("\nEnter で次へ > ")
    return ctx

def plot_refine_dialogue(ctx):
    asyncio.run(refine_dialog(ctx, ctx.get("purpose","プロット")))
    return ctx

# generate dummy process functions
def _make_process(n):
    def _proc(ctx):
        print(f"PROCESS{n}: ダミー処理")
        time.sleep(0.1)
        return ctx
    _proc.__name__ = f"process_{n}"
    return _proc
globals().update({f"process_{i}": _make_process(i) for i in range(1,24)})

def fermi_evaluate(ctx):
    prob = random.randint(70,99)
    print(f"読了確率を推定: {prob}%")
    ctx["read_prob"]=prob
    return ctx

def rewrite_needed(ctx):
    return "lt90" if ctx.get("read_prob",0)<90 else "gte90"

def feedback_analysis(ctx):
    print("フィードバック分析…(ダミー)")
    return ctx

def rewrite_cycle(ctx):
    count = ctx.get("rewrite_count",0)+1
    ctx["rewrite_count"]=count
    print(f"書き直しサイクル {count}")
    return ctx

# ------------- Engine -------------
def run():
    ctx={}
    node_id="START"
    loop_counts={}
    while node_id!="END":
        node=graph["nodes"][node_id]
        func_name=node.get("func")
        if func_name:
            ctx=globals()[func_name](ctx)
        if "branch" in node:
            branch_key=node["branch"]
            choice=globals()[branch_key](ctx)
            node_id=branches[branch_key][choice]
        else:
            node_id=node.get("next")
        # loop guard
        if node_id=="REWRITE":
            count=ctx.get("rewrite_count",0)
            if count>=graph["nodes"]["REWRITE"].get("loop_max",15):
                node_id="END"
    print("\n=== 完了 ===")

if __name__ == "__main__":
    run()
