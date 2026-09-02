import sys
sys.path.insert(0, '/app')
import asyncio
from logic.data.soup_llm import llm_atomize_facts, llm_judge_question, llm_generate_hint

async def test():
    surface = "一个人在沙漠中走了很久，他划燃一根火柴，然后死了"
    bottom = "一个男子在沙漠中迷路，他决定用火柴数数来计算自己走了多少步。他划燃一根火柴，然后在火柴熄灭前数到20，这样他就知道自己走了20步。但后来他发现火柴盒里只剩最后一根火柴，他绝望地自杀了。"

    print("=== 测试1: 事实原子化 ===")
    facts = await llm_atomize_facts(surface, bottom)
    print("事实清单:", facts[:3], "...")

    print()
    print("=== 测试2: 问题判断 ===")
    result = await llm_judge_question(surface, bottom, facts, "问他是自杀的吗？", [])
    t = result["type"]
    c = result["content"]
    print("类型:", t)
    print("回答:", c)

    print()
    print("=== 测试3: 生成提示 ===")
    hint = await llm_generate_hint(surface, bottom, facts, [])
    print("提示:", hint)

    print()
    print("=== 全部测试通过 ===")

asyncio.run(test())