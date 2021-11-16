import sqlite3
import sys
from dataclasses import dataclass, field
from typing import Iterator, List

from . import migrations
from .models import Package

migrations_pipeline = [
    ("0001", "create_package_table"),
]


@dataclass
class Storage:
    _executed_migrations: list = field(default_factory=list)

    def __post_init__(self):
        self.con = sqlite3.connect("elskg_bot.db")
        self.check_migrations()

    def check_migrations(self):
        with self.con:
            self.con.execute(migrations.migrations_table)
            cur = self.con.cursor()
            migrations_map = dict(migrations_pipeline)
            for row in cur.execute("SELECT name FROM migration order by name;"):
                self._executed_migrations.append(row[0])
                migrations_map.pop(row[0], None)

        if not migrations_map:
            return

        if "run_migrations" in sys.argv:
            return

        print(f"You need to execute the next migrations:")
        for migration_number, migration_name in migrations_map.items():
            print(f"[{migration_number}] {migration_name}")

    def run_migrations(self):
        for migration_number, migration_name in migrations_pipeline:
            if migration_number in self._executed_migrations:
                continue

            migration_sql = getattr(migrations, migration_name)
            with self.con:
                self.con.execute(migration_sql)
                self.con.execute("INSERT INTO migration VALUES (?)", (migration_number,))
                self._executed_migrations.append(migration_number)
            print(f"[{migration_number}] {migration_name} \t OK!")

    def add_package(self, package: Package):
        with self.con:
            cur = self.con.cursor()
            count = list(cur.execute(
                "SELECT count(*) FROM package WHERE chat_id = ? and tracking = ?",
                (package.chat_id, package.tracking),
            ))[0]
            if count[0] != 0:
                return
            self.con.execute("INSERT INTO package VALUES (?, ?, ?, ?)", package.as_tuple())

    _non_notified_sql = """SELECT chat_id, tracking, status_text, notified FROM package WHERE notified is false;"""

    def fetch_non_notified_package(self) -> Iterator[Package]:
        with self.con:
            cur = self.con.cursor()
            for row in cur.execute(self._non_notified_sql):
                yield Package.from_row(*row)

    _my_packages_sql = """SELECT chat_id, tracking, status_text, notified FROM package WHERE chat_id = ?"""

    def fetch_my_packages(self, chat_id: int) -> Iterator[Package]:
        with self.con:
            cur = self.con.cursor()
            for row in cur.execute(self._my_packages_sql, (chat_id,)):
                yield Package.from_row(*row)

    _update_package_sql = """UPDATE package set status_text = ?, notified = ? WHERE tracking = ? and chat_id = ?"""

    def bulk_update_packages(self, packages: "List[Package]"):
        with self.con:
            for p in packages:
                args = (p.status_text, p.notified, p.tracking, p.chat_id)
                self.con.execute(self._update_package_sql, args)


storage = Storage()
