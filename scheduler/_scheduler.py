import asyncio
import time
from dataclasses import dataclass

import schedule

from db import storage
from scheduler.helpers import check_packages
from telegram import bot


@dataclass
class Scheduler:

    def __post_init__(self):
        self._register_tasks()

    def _register_tasks(self):
        # schedule.every().hour.do(self.check_packages_task)
        schedule.every().minute.do(self.check_packages_task)

    def check_packages_task(self):
        print("Start [check_packages_task].")
        all_packages = list(storage.fetch_non_notified_package())
        packages_tracks = [i.tracking for i in all_packages]
        statuses_map = asyncio.run(check_packages(packages_tracks))

        print("Prepare to update [check_packages_task].")
        to_update = []
        for package in all_packages:
            status = statuses_map[package.tracking]
            if package.status_text == status:
                continue

            package.status_text = status
            if not package.status_text_is_default:
                asyncio.run(bot.notification_change_status(package))
                package.notified = True

            to_update.append(package)

        print("Update [check_packages_task].")
        storage.bulk_update_packages(to_update)

    def start(self):
        while True:
            schedule.run_pending()
            time.sleep(1)


scheduler = Scheduler()
