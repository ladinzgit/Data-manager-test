import unittest
import os
from datetime import datetime, timedelta
from DataManager import DataManager

class TestDataManager(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.db_path = "test_voice_logs.db"
        self.dm = DataManager(self.db_path)
        await self.dm.ensure_initialized()

    async def asyncTearDown(self):
        await self.dm.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    async def test_register_and_get_tracked_channel(self):
        # 여러 개 등록, 중복 등록 테스트
        await self.dm.register_tracked_channel(12345, 'test_source')
        await self.dm.register_tracked_channel(67890, 'test_source')
        await self.dm.register_tracked_channel(12345, 'test_source')  # 중복 등록
        channels = await self.dm.get_tracked_channels('test_source')
        self.assertIn(12345, channels)
        self.assertIn(67890, channels)
        self.assertEqual(channels.count(12345), 1)  # 중복 없음

    async def test_unregister_and_get_tracked_channel(self):
        await self.dm.register_tracked_channel(11111, 'src')
        await self.dm.register_tracked_channel(22222, 'src')
        await self.dm.unregister_tracked_channel(11111, 'src')
        channels = await self.dm.get_tracked_channels('src')
        self.assertNotIn(11111, channels)
        self.assertIn(22222, channels)

    async def test_unregister_nonexistent_channel(self):
        # 없는 채널 해제해도 에러가 없어야 함
        try:
            await self.dm.unregister_tracked_channel(99999, 'src')
        except Exception as e:
            self.fail(f"Unregistering nonexistent channel raised Exception: {e}")

    async def test_add_and_get_voice_time(self):
        await self.dm.add_voice_time(1, 123, 3600)
        await self.dm.add_voice_time(1, 123, 10)  # 누적
        result, _, _ = await self.dm.get_user_times(1, '일간', datetime.now())
        self.assertEqual(result.get(123), 3610)

        # 기록 없는 경우
        result_empty, _, _ = await self.dm.get_user_times(2, '일간', datetime.now())
        self.assertEqual(result_empty, {})

    async def test_deleted_channel_handling(self):
        await self.dm.register_deleted_channel(789, 456)
        category_id = await self.dm.get_deleted_channel_category(789)
        self.assertEqual(category_id, 456)

    async def test_deleted_channel_not_exist(self):
        category_id = await self.dm.get_deleted_channel_category(999)
        self.assertIsNone(category_id)

if __name__ == '__main__':
    unittest.main()
