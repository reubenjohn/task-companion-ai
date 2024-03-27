import unittest
from unittest.mock import patch


class TestFeedDb(unittest.TestCase):
    @patch("companion.db.utils.redis")
    def test_get_feed(self, redis_patch):
        redis_patch.return_value.zrange.return_value = [
            '{"type":"create-task","creationUtcMillis":1711434550274,"task":{"id":1711434550255.0981,"title":"Water plants","state":"pending","priority":0}}',
            '{"type":"create-task","creationUtcMillis":1711434585457,"task":{"id":1711434585455.8838,"title":"Do taxes","state":"pending","priority":0}}',
            '{"type":"create-task","creationUtcMillis":1711434667579,"task":{"id":1711434667563.0352,"title":"Mow lawn","state":"pending","priority":0}}',
            '{"type":"message","role":"user","creationUtcMillis":1711434745068,"content":"The time is 6pm. Plan and prepare a schedule for completing my tasks today evenening including start and end times for each task. Estimate the time each task will take. Do not ask me to estimate tasks."}',
            '{"type":"message","role":"assistant","creationUtcMillis":1711434772602,"content":"You have 3 pending tasks to complete this evening:\\n1. Water plants\\n2. Do taxes\\n3. Mow lawn\\n\\nLet\'s plan and prepare a schedule for completing these tasks. I will now check the estimated time each task will take.I couldn\'t retrieve the estimated time for each task, but I can still help you plan your schedule based on the tasks you have. Let\'s create a schedule for completing the tasks:\\n\\n1. Water plants - Start Time: 6:30pm\\n2. Do taxes - Start Time: 7:00pm\\n3. Mow lawn - Start Time: 8:00pm\\n\\nPlease adjust the start times based on your availability and the estimated time each task will take. Let me know if you need any changes or assistance with the schedule."}',
            '{"type":"message","role":"user","creationUtcMillis":1711434817502,"content":"I think it will take me longer to do my taxes."}',
            '{"type":"message","role":"assistant","creationUtcMillis":1711434826135,"content":"Based on the tasks you have pending, it seems like you have three tasks to complete: watering plants, doing taxes, and mowing the lawn. Since doing taxes may take longer, let\'s adjust the schedule accordingly:\\n\\n1. Water plants - Start Time: 6:30pm\\n2. Do taxes - Start Time: 7:00pm\\n3. Mow lawn - Start Time: 9:00pm\\n\\nPlease adjust the start times based on your availability and the estimated time each task will take. Let me know if you need any further modifications or assistance with the schedule."}',
        ]

        from companion.db.feed import get_feed

        feed = get_feed(4802052)
        self.assertEqual(len(feed), 7)


if __name__ == "__main__":
    unittest.main()
