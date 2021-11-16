"""Migrations."""

migrations_table = """CREATE TABLE IF NOT EXISTS migration (name text)"""

create_package_table = """CREATE TABLE IF NOT EXISTS package (chat_id int, tracking text, status_text text, notified boolean)"""
