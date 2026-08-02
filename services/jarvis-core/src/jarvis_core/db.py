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
  prompt_content text not null default '',
  sandbox_mode text not null,
  approval_required integer not null,
  approval_id text,
  risk_level text not null,
  risk_reasons text not null,
  created_at text not null,
  updated_at text not null
);

create table if not exists codex_executions (
  execution_id text primary key,
  plan_id text not null,
  task_id text not null,
  project_name text not null,
  status text not null,
  started_at text not null,
  finished_at text,
  codex_command_preview text not null,
  exit_code integer,
  stdout_excerpt text,
  stderr_excerpt text,
  output_path text,
  receipt_id text,
  blocked_reason text,
  error text,
  post_review text not null default '{}',
  check_plan text not null default '{}',
  check_results text not null default '{}',
  repair_results text not null default '{}'
);

create table if not exists validation_runs (
  run_id text primary key,
  runbook_id text not null,
  status text not null,
  target_environment text not null,
  created_at text not null,
  updated_at text not null,
  started_at text,
  completed_at text,
  summary text not null default ''
);

create table if not exists validation_step_results (
  id integer primary key autoincrement,
  run_id text not null,
  step_id text not null,
  status text not null,
  notes text not null default '',
  redacted_evidence text not null default '',
  updated_at text not null,
  unique(run_id, step_id),
  foreign key(run_id) references validation_runs(run_id)
);

create table if not exists memories (
  memory_id text primary key,
  memory_type text not null,
  content text not null,
  status text not null,
  scope_type text not null,
  scope_value text,
  source_type text not null,
  source_agent_id text,
  source_reference text,
  proposal_reason text,
  confidence text not null,
  sensitivity text not null,
  expires_at text,
  created_at text not null,
  updated_at text not null,
  approved_at text,
  approved_by text,
  last_confirmed_at text,
  disabled_at text,
  rejected_at text,
  rejected_by text,
  rejection_reason text,
  content_hash text not null
);

create table if not exists memory_events (
  event_id text primary key,
  memory_id text not null,
  event_type text not null,
  actor text not null,
  metadata text not null,
  created_at text not null
);

create table if not exists memory_retrievals (
  retrieval_id text primary key,
  purpose text not null,
  agent_id text,
  project_name text,
  query_hash text not null,
  query_term_count integer not null,
  include_sensitive integer not null,
  retrieval_mode text not null,
  candidate_count integer not null,
  selected_count integer not null,
  created_at text not null
);

create table if not exists memory_retrieval_items (
  retrieval_id text not null,
  memory_id text not null,
  memory_type text not null,
  scope_type text not null,
  rank integer not null,
  text_score numeric not null,
  scope_priority integer not null,
  confidence_priority integer not null,
  created_at text not null,
  unique(retrieval_id, memory_id)
);

create index if not exists idx_memories_status on memories(status);
create index if not exists idx_memories_memory_type on memories(memory_type);
create table if not exists response_feedback (
  feedback_id text primary key,
  response_id text not null unique,
  agent_id text not null,
  rating text not null,
  issue_tags text not null,
  note text not null default '',
  linked_memory_id text,
  created_at text not null,
  updated_at text not null
);

create table if not exists feedback_events (
  event_id text primary key,
  feedback_id text not null,
  event_type text not null,
  actor text not null,
  metadata text not null,
  created_at text not null
);

create table if not exists knowledge_sources (
  source_id text primary key,
  title text not null,
  source_type text not null,
  status text not null,
  scope_type text not null,
  scope_value text,
  sensitivity text not null,
  media_type text not null,
  project_name text,
  relative_path text,
  content text not null,
  content_hash text not null,
  tags text not null,
  char_count integer not null,
  chunk_count integer not null,
  source_size_bytes integer,
  source_modified_at text,
  created_at text not null,
  updated_at text not null,
  imported_at text not null,
  disabled_at text
);

create table if not exists knowledge_chunks (
  chunk_id text primary key,
  source_id text not null,
  chunk_index integer not null,
  content text not null,
  content_hash text not null,
  char_start integer not null,
  char_end integer not null,
  created_at text not null,
  unique(source_id, chunk_index)
);

create table if not exists knowledge_events (
  event_id text primary key,
  source_id text not null,
  event_type text not null,
  actor text not null,
  metadata text not null,
  created_at text not null
);

create table if not exists knowledge_retrievals (
  retrieval_id text primary key,
  purpose text not null,
  agent_id text,
  project_name text,
  query_hash text not null,
  query_term_count integer not null,
  include_sensitive integer not null,
  retrieval_mode text not null,
  candidate_chunk_count integer not null,
  candidate_source_count integer not null,
  selected_chunk_count integer not null,
  selected_source_count integer not null,
  created_at text not null
);

create table if not exists knowledge_retrieval_items (
  retrieval_id text not null,
  chunk_id text not null,
  source_id text not null,
  rank integer not null,
  text_score real not null,
  scope_priority integer not null,
  source_rank integer not null,
  chunk_index integer not null,
  created_at text not null,
  unique(retrieval_id, chunk_id)
);
create table if not exists knowledge_embedding_settings (
  settings_id text primary key,
  enabled integer not null,
  provider text not null,
  model_name text,
  active_profile_id text,
  dimensions integer,
  configured_at text,
  updated_at text not null
);

create table if not exists knowledge_embedding_profiles (
  profile_id text primary key,
  provider text not null,
  model_name text not null,
  dimensions integer not null,
  normalization text not null,
  created_at text not null,
  last_used_at text,
  unique(provider, model_name, dimensions)
);

create table if not exists knowledge_chunk_embeddings (
  profile_id text not null,
  chunk_id text not null,
  source_id text not null,
  content_hash text not null,
  dimensions integer not null,
  vector blob not null,
  created_at text not null,
  updated_at text not null,
  unique(profile_id, chunk_id)
);

create table if not exists knowledge_embedding_runs (
  run_id text primary key,
  operation text not null,
  profile_id text,
  provider text not null,
  model_name text,
  requested_chunk_count integer not null,
  embedded_chunk_count integer not null,
  skipped_chunk_count integer not null,
  failed_chunk_count integer not null,
  include_sensitive integer not null,
  source_id text,
  status text not null,
  error_code text,
  created_at text not null,
  completed_at text
);

create table if not exists knowledge_retrieval_scores (
  retrieval_id text not null,
  chunk_id text not null,
  profile_id text,
  lexical_rank integer,
  semantic_rank integer,
  semantic_score real,
  hybrid_score real,
  created_at text not null,
  unique(retrieval_id, chunk_id)
);

create table if not exists local_generation_settings (
  settings_id text primary key,
  enabled integer not null,
  provider text not null,
  model_name text,
  active_profile_id text,
  context_char_limit integer not null,
  max_output_chars integer not null,
  default_temperature real not null,
  keep_alive_seconds integer not null,
  configured_at text,
  updated_at text not null
);

create table if not exists local_generation_profiles (
  profile_id text primary key,
  provider text not null,
  model_name text not null,
  context_char_limit integer not null,
  max_output_chars integer not null,
  default_temperature real not null,
  keep_alive_seconds integer not null,
  structured_output_mode text not null,
  created_at text not null,
  last_used_at text
);

create table if not exists local_generation_runs (
  run_id text primary key,
  response_id text,
  agent_id text,
  purpose text not null,
  profile_id text,
  provider text not null,
  model_name text,
  requested_mode text not null,
  actual_mode text not null,
  output_style text not null,
  status text not null,
  prompt_hash text,
  prompt_char_count integer not null,
  current_request_char_count integer not null,
  deterministic_response_char_count integer not null,
  memory_item_count integer not null,
  knowledge_chunk_count integer not null,
  web_source_count integer not null,
  prior_context_present integer not null,
  section_stats text not null,
  output_char_count integer not null,
  fallback_used integer not null,
  thinking_discarded integer not null,
  error_code text,
  created_at text not null,
  completed_at text
);
create index if not exists idx_memories_scope on memories(scope_type, scope_value);
create index if not exists idx_memories_expiration on memories(expires_at);
create index if not exists idx_memories_content_hash on memories(content_hash);
create index if not exists idx_memory_events_memory_date on memory_events(memory_id, created_at);
create index if not exists idx_memory_retrievals_date on memory_retrievals(created_at);
create index if not exists idx_memory_retrievals_agent_date on memory_retrievals(agent_id, created_at);
create index if not exists idx_memory_retrievals_project_date on memory_retrievals(project_name, created_at);
create index if not exists idx_memory_retrieval_items_memory on memory_retrieval_items(memory_id);
create index if not exists idx_response_feedback_created on response_feedback(created_at);
create index if not exists idx_response_feedback_agent_date on response_feedback(agent_id, created_at);
create index if not exists idx_response_feedback_rating_date on response_feedback(rating, created_at);
create index if not exists idx_response_feedback_linked_memory on response_feedback(linked_memory_id);
create index if not exists idx_feedback_events_feedback_date on feedback_events(feedback_id, created_at);
create index if not exists idx_memory_retrieval_items_rank on memory_retrieval_items(retrieval_id, rank);
create index if not exists idx_knowledge_sources_status on knowledge_sources(status);
create index if not exists idx_knowledge_sources_type on knowledge_sources(source_type);
create index if not exists idx_knowledge_sources_scope on knowledge_sources(scope_type, scope_value);
create index if not exists idx_knowledge_sources_sensitivity on knowledge_sources(sensitivity);
create index if not exists idx_knowledge_sources_project on knowledge_sources(project_name);
create index if not exists idx_knowledge_sources_content_hash on knowledge_sources(content_hash);
create index if not exists idx_knowledge_sources_updated on knowledge_sources(updated_at);
create index if not exists idx_knowledge_chunks_source_index on knowledge_chunks(source_id, chunk_index);
create index if not exists idx_knowledge_chunks_content_hash on knowledge_chunks(content_hash);
create index if not exists idx_knowledge_events_source_date on knowledge_events(source_id, created_at);
create index if not exists idx_knowledge_retrievals_date on knowledge_retrievals(created_at);
create index if not exists idx_knowledge_retrievals_agent_date on knowledge_retrievals(agent_id, created_at);
create index if not exists idx_knowledge_retrievals_project_date on knowledge_retrievals(project_name, created_at);
create index if not exists idx_knowledge_retrievals_purpose_date on knowledge_retrievals(purpose, created_at);
create index if not exists idx_knowledge_retrieval_items_source on knowledge_retrieval_items(source_id);
create index if not exists idx_knowledge_retrieval_items_chunk on knowledge_retrieval_items(chunk_id);
create index if not exists idx_knowledge_retrieval_items_rank on knowledge_retrieval_items(retrieval_id, rank);
create index if not exists idx_knowledge_embedding_settings_profile on knowledge_embedding_settings(active_profile_id);
create index if not exists idx_knowledge_chunk_embeddings_chunk on knowledge_chunk_embeddings(chunk_id);
create index if not exists idx_knowledge_chunk_embeddings_source on knowledge_chunk_embeddings(source_id);
create index if not exists idx_knowledge_chunk_embeddings_hash on knowledge_chunk_embeddings(content_hash);
create index if not exists idx_knowledge_chunk_embeddings_profile_source on knowledge_chunk_embeddings(profile_id, source_id);
create index if not exists idx_knowledge_embedding_runs_date on knowledge_embedding_runs(created_at);
create index if not exists idx_knowledge_embedding_runs_status on knowledge_embedding_runs(status);
create index if not exists idx_knowledge_retrieval_scores_retrieval on knowledge_retrieval_scores(retrieval_id);
create index if not exists idx_knowledge_retrieval_scores_chunk on knowledge_retrieval_scores(chunk_id);
create index if not exists idx_local_generation_runs_date on local_generation_runs(created_at);
create index if not exists idx_local_generation_runs_agent_date on local_generation_runs(agent_id, created_at);
create index if not exists idx_local_generation_runs_status_date on local_generation_runs(status, created_at);
create index if not exists idx_local_generation_runs_profile_date on local_generation_runs(profile_id, created_at);
create index if not exists idx_local_generation_runs_response on local_generation_runs(response_id);

create trigger if not exists knowledge_chunk_embeddings_delete
after delete on knowledge_chunks begin
  delete from knowledge_chunk_embeddings where chunk_id = old.chunk_id;
end;
"""

_MEMORY_FTS_COLUMNS = """
  memory_id unindexed,
  content,
  memory_type,
  scope_type,
  scope_value,
  source_type,
  source_agent_id,
  source_reference,
  proposal_reason,
  tokenize = 'unicode61'
"""

_KNOWLEDGE_FTS_COLUMNS = """
  chunk_id unindexed,
  source_id unindexed,
  content,
  source_title,
  tags,
  scope_type,
  scope_value,
  tokenize = 'unicode61'
"""


def init_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.executescript(SCHEMA)
    conn.execute(
        """
        insert or ignore into knowledge_embedding_settings (
          settings_id, enabled, provider, model_name, active_profile_id,
          dimensions, configured_at, updated_at
        ) values ('default', 0, 'ollama_local', null, null, null, null, current_timestamp)
        """
    )
    conn.execute(
        """
        insert or ignore into local_generation_settings (
          settings_id, enabled, provider, model_name, active_profile_id,
          context_char_limit, max_output_chars, default_temperature,
          keep_alive_seconds, configured_at, updated_at
        ) values ('default', 0, 'ollama_local', null, null, 24000, 4000, 0.2, 300, null, current_timestamp)
        """
    )
    _ensure_column(conn, "codex_plans", "prompt_content", "text not null default ''")
    _ensure_column(conn, "codex_executions", "post_review", "text not null default '{}'")
    _ensure_column(conn, "codex_executions", "check_plan", "text not null default '{}'")
    _ensure_column(conn, "codex_executions", "check_results", "text not null default '{}'")
    _ensure_column(conn, "codex_executions", "repair_results", "text not null default '{}'")
    _initialize_memory_fts(conn)
    _initialize_knowledge_fts(conn)
    conn.commit()
    return conn


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = {row[1] for row in conn.execute(f"pragma table_info({table})").fetchall()}
    if column not in columns:
        conn.execute(f"alter table {table} add column {column} {definition}")


def _initialize_memory_fts(conn: sqlite3.Connection) -> bool:
    try:
        conn.execute(f"create virtual table if not exists memory_fts using fts5({_MEMORY_FTS_COLUMNS})")
        conn.executescript(
            """
            create trigger if not exists memories_fts_insert
            after insert on memories begin
              insert into memory_fts (
                rowid, memory_id, content, memory_type, scope_type, scope_value,
                source_type, source_agent_id, source_reference, proposal_reason
              ) values (
                new.rowid, new.memory_id, new.content, new.memory_type, new.scope_type,
                coalesce(new.scope_value, ''), new.source_type,
                coalesce(new.source_agent_id, ''), coalesce(new.source_reference, ''),
                coalesce(new.proposal_reason, '')
              );
            end;

            create trigger if not exists memories_fts_update
            after update on memories begin
              delete from memory_fts where rowid = old.rowid;
              insert into memory_fts (
                rowid, memory_id, content, memory_type, scope_type, scope_value,
                source_type, source_agent_id, source_reference, proposal_reason
              ) values (
                new.rowid, new.memory_id, new.content, new.memory_type, new.scope_type,
                coalesce(new.scope_value, ''), new.source_type,
                coalesce(new.source_agent_id, ''), coalesce(new.source_reference, ''),
                coalesce(new.proposal_reason, '')
              );
            end;

            create trigger if not exists memories_fts_delete
            after delete on memories begin
              delete from memory_fts where rowid = old.rowid;
            end;
            """
        )
        conn.execute("delete from memory_fts")
        conn.execute(
            """
            insert into memory_fts (
              rowid, memory_id, content, memory_type, scope_type, scope_value,
              source_type, source_agent_id, source_reference, proposal_reason
            )
            select
              rowid, memory_id, content, memory_type, scope_type, coalesce(scope_value, ''),
              source_type, coalesce(source_agent_id, ''), coalesce(source_reference, ''),
              coalesce(proposal_reason, '')
            from memories
            """
        )
        return True
    except sqlite3.OperationalError as exc:
        if "fts5" not in str(exc).lower():
            raise
        return False


def memory_fts5_available(conn: sqlite3.Connection) -> bool:
    try:
        conn.execute("select count(*) from memory_fts").fetchone()
        return True
    except sqlite3.OperationalError:
        return False

def _initialize_knowledge_fts(conn: sqlite3.Connection) -> bool:
    try:
        conn.execute(
            f"create virtual table if not exists knowledge_chunks_fts using fts5({_KNOWLEDGE_FTS_COLUMNS})"
        )
        conn.executescript(
            """
            create trigger if not exists knowledge_chunks_fts_insert
            after insert on knowledge_chunks begin
              insert into knowledge_chunks_fts (
                chunk_id, source_id, content, source_title, tags, scope_type, scope_value
              )
              select
                new.chunk_id, new.source_id, new.content, source.title, source.tags,
                source.scope_type, coalesce(source.scope_value, '')
              from knowledge_sources as source
              where source.source_id = new.source_id;
            end;

            create trigger if not exists knowledge_chunks_fts_update
            after update on knowledge_chunks begin
              delete from knowledge_chunks_fts where chunk_id = old.chunk_id;
              insert into knowledge_chunks_fts (
                chunk_id, source_id, content, source_title, tags, scope_type, scope_value
              )
              select
                new.chunk_id, new.source_id, new.content, source.title, source.tags,
                source.scope_type, coalesce(source.scope_value, '')
              from knowledge_sources as source
              where source.source_id = new.source_id;
            end;

            create trigger if not exists knowledge_chunks_fts_delete
            after delete on knowledge_chunks begin
              delete from knowledge_chunks_fts where chunk_id = old.chunk_id;
            end;
            """
        )
        conn.execute("delete from knowledge_chunks_fts")
        conn.execute(
            """
            insert into knowledge_chunks_fts (
              chunk_id, source_id, content, source_title, tags, scope_type, scope_value
            )
            select
              chunk.chunk_id, chunk.source_id, chunk.content, source.title, source.tags,
              source.scope_type, coalesce(source.scope_value, '')
            from knowledge_chunks as chunk
            join knowledge_sources as source on source.source_id = chunk.source_id
            order by chunk.source_id, chunk.chunk_index
            """
        )
        return True
    except sqlite3.OperationalError as exc:
        if "fts5" not in str(exc).lower():
            raise
        return False


def knowledge_fts5_available(conn: sqlite3.Connection) -> bool:
    try:
        conn.execute("select count(*) from knowledge_chunks_fts").fetchone()
        return True
    except sqlite3.OperationalError:
        return False
