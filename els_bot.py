#!/usr/bin/env python
import sys


def main():
    match sys.argv:
        case [*a, "run_bot"]:
            from telegram import bot

            bot.start_polling()
        case [*a, "run_migrations"]:
            from db import storage

            storage.run_migrations()
        case [*a, "run_scheduler"]:
            from scheduler import scheduler

            scheduler.start()
        case _:
            print(sys.argv)


if __name__ == '__main__':
    main()
