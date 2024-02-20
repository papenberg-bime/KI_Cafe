import platform
from vendor.ur_robotiq_gripper import Gripper
import asyncio
import sys
sys.path.append('.')


if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class GripperStatus:

    def __init__(self, HOST):
        self.gripper = Gripper(HOST)
        self.loop = asyncio.get_event_loop()
        self.run_sync(self.gripper.connect())

    def run_sync(self, coroutine):
        return self.loop.run_until_complete(coroutine)

    def get_position(self):
        return self.run_sync(self.gripper.get_current_position())
