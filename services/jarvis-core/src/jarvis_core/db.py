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

create table if not exists tasks (
  task_id text primary key,
  project_name text not null,
  agent_id text not null,
  task_type text not null,
  status text not null,
  autonomy_level text not null,
  dry_run integer not null,
  write_capable integer not null default 0,
  created_at text not null,
  started_at text,
  finished_at text,
  summary text,
  error text
);

create table if not exists events (
  event_id text primary key,
  task_id text,
  event_type text not null,
  payload text not null,
  created_at text not null
);

create table if not exists approvals (
  approval_id text primary key,
  task_id text,
  action_id text,
  action_type text not null,
  project_name text,
  risk_level text not null,
  reason text not null,
  status text not null,
  requested_at text not null,
  resolved_at text,
  resolved_by text,
  resolution_note text
);

create table if not exists action_receipts (
  receipt_id text primary key,
  task_id text,
  agent_id text not null,
  tool_id text not null,
  action_type text not null,
  target text,
  approved integer not null,
  blocked integer not null,
  approval_required integer not null,
  risk_level text not null,
  started_at text not null,
  finished_at text not null,
  result text,
  reason text not null
);

create table if not exists project_locks (
  project_name text primary key,
  task_id text not null,
  lock_type text not null,
  locked_at text not null
);

create table if not exists codex_plans (
  plan_id text primary key,
  task_id text not null,
  project_name text not null,
  agent_id text not null,
  tool_id text not null,
  action_type text not null,
  mode text not null,
  status text not null,
  project_path text not null,
  prompt_path text not null,
  output_path text not null,
  command_template text not null,
  command_preview text not null,
  sandbox_mode text not null,
  approval_required integer not null,
  approval_id text,
  risk_level text not null,
  risk_reasons text not null,
  created_at text not null,
  updated_at text not null
);
"""


def init_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    conn.commit()
    return conn
