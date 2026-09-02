"""海龟汤 LLM 的无外网回归测试。"""

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from logic.data import soup_llm  # noqa: E402


class SoupLlmTests(unittest.IsolatedAsyncioTestCase):
    def test_extracts_allowed_answers(self):
        self.assertEqual(
            soup_llm._extract_answer("是，这个细节与汤底一致"),
            {"type": "answer", "content": "是"},
        )
        self.assertEqual(
            soup_llm._extract_answer("否。"),
            {"type": "answer", "content": "不是"},
        )

    def test_history_is_bounded(self):
        history = [
            {"role": "user", "content": "x" * 3000},
            {"role": "assistant", "content": "y" * 3000},
        ] * 20
        formatted = soup_llm._format_history(history)
        self.assertLessEqual(len(formatted), 12000)

    async def test_codex_success_is_post_processed(self):
        fake_config = {"soup_llm": {"backend": "codex"}}
        with (
            patch.object(soup_llm, "config", fake_config),
            patch.object(soup_llm, "_codex_chat", AsyncMock(return_value="无关，这与故事无关")),
        ):
            result = await soup_llm.llm_judge_question("汤面", "汤底", "问天气有关吗？", [])
        self.assertEqual(result, {"type": "answer", "content": "无关"})

    async def test_codex_failure_falls_back_without_network(self):
        fake_config = {"soup_llm": {"backend": "codex"}}
        with (
            patch.object(soup_llm, "config", fake_config),
            patch.object(soup_llm, "_codex_chat", AsyncMock(return_value=None)),
            patch.object(
                soup_llm,
                "_llm_chat",
                AsyncMock(return_value={"content": "不是，与汤底矛盾", "usage": None}),
            ),
        ):
            result = await soup_llm.llm_judge_question("汤面", "汤底", "问是这样吗？", [])
        self.assertEqual(result, {"type": "answer", "content": "不是"})


if __name__ == "__main__":
    unittest.main()
