"""LRobot 有界资源的无外网回归测试。"""

import asyncio
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import FutureManager  # noqa: E402


class FutureManagerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.manager = FutureManager(early_ttl=0.05, early_max=32)
        self.manager.init(asyncio.get_running_loop())

    async def test_wait_then_set_is_removed(self):
        waiter = asyncio.create_task(self.manager.wait("normal", timeout=1))
        await asyncio.sleep(0)
        self.manager.set("normal", {"ok": True})
        self.assertEqual(await waiter, {"ok": True})
        self.assertEqual(self.manager.stats()["pending"], 0)

    async def test_set_then_wait_is_consumed(self):
        self.manager.set("early", "done")
        await asyncio.sleep(0)
        self.assertEqual(await self.manager.wait("early", timeout=1), "done")
        self.assertEqual(self.manager.stats()["early"], 0)

    async def test_timeout_cleans_pending(self):
        with self.assertRaises(TimeoutError):
            await self.manager.wait("timeout", timeout=0.01)
        self.assertEqual(self.manager.stats()["pending"], 0)

    async def test_cancel_cleans_pending(self):
        waiter = asyncio.create_task(self.manager.wait("cancel", timeout=1))
        await asyncio.sleep(0)
        waiter.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await waiter
        self.assertEqual(self.manager.stats()["pending"], 0)

    async def test_thread_callback_reaches_loop(self):
        waiter = asyncio.create_task(self.manager.wait("thread", timeout=1))
        await asyncio.sleep(0)
        await asyncio.to_thread(self.manager.set, "thread", "done")
        self.assertEqual(await waiter, "done")
        self.assertEqual(self.manager.stats()["pending"], 0)

    async def test_duplicate_early_key_keeps_latest_value(self):
        self.manager.set("duplicate", "old")
        self.manager.set("duplicate", "new")
        self.assertEqual(self.manager.stats()["early"], 1)
        self.assertEqual(await self.manager.wait("duplicate", timeout=1), "new")

    async def test_early_results_are_bounded_and_expire(self):
        for index in range(1000):
            self.manager.set(f"key-{index}", index)
        await asyncio.sleep(0)
        self.assertLessEqual(self.manager.stats()["early"], 32)
        await asyncio.sleep(0.06)
        self.assertEqual(self.manager.stats()["early"], 0)

    async def test_early_exception_reaches_waiter_and_is_removed(self):
        self.manager.set_exception("failed", RuntimeError("queue full"))
        await asyncio.sleep(0)
        with self.assertRaisesRegex(RuntimeError, "queue full"):
            await self.manager.wait("failed", timeout=1)
        self.assertEqual(self.manager.stats()["early"], 0)


if __name__ == "__main__":
    unittest.main()
