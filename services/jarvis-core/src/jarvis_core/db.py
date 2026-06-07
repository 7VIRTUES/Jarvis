from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA = """
create table if not exists projects (
  id integer primary key autoincrement,
  name text not null unique,
  path text not null,
  created_at text not null default current_timestamp
);

create table if not exists action_events (
  id integer primary key autoincrement,
  action_id text not null,
  status text not null,
  reason text,
  created_at text not null default current_timestamp
);

create table if not exists security_events (
  id integer primary key autoincrement,
  event_type text not null,
  detail text not null,
  created_at text not null default current_timestamp
);

create table if not exists registry_metadata (
  id integer primary key autoincrement,
  registry_type text not null,
  name text not null,
  version text,
  created_at text not null default current_timestamp
);
"""


def init_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    conn.commit()
    return conn

