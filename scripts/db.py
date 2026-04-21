import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from dotenv import load_dotenv
import uuid

load_dotenv()

# --- Gemini Pricing (USD per 1M tokens) ---
PRICING = {
    "gemini-2.5-pro": {
        "input": 1.25,
        "output": 10.00,
    },
    "gemini-2.5-flash": {
        "input": 0.15,
        "output": 0.60,
    }
}

def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    p = PRICING.get(model, {"input": 0, "output": 0})
    return round(
        (input_tokens / 1_000_000 * p["input"]) +
        (output_tokens / 1_000_000 * p["output"]),
        6
    )

class Database:
    def __init__(self):
        self.conn_str = os.getenv("POSTGRES_URL")
        if not self.conn_str:
            raise ValueError("POSTGRES_URL not found in environment")
        self.conn = psycopg2.connect(self.conn_str)
        self.conn.autocommit = True

    def get_cursor(self):
        return self.conn.cursor(cursor_factory=RealDictCursor)

    # --- Pipeline Runs ---
    def create_run(self, triggered_by, trigger_source=None):
        with self.get_cursor() as cur:
            cur.execute(
                "INSERT INTO pipeline_runs (triggered_by, trigger_source) VALUES (%s, %s) RETURNING run_id",
                (triggered_by, trigger_source)
            )
            return cur.fetchone()['run_id']

    def complete_run(self, run_id, status, files_found, files_processed, files_skipped, files_failed, error_message=None):
        with self.get_cursor() as cur:
            cur.execute(
                """UPDATE pipeline_runs SET 
                   status = %s, files_found = %s, files_processed = %s, 
                   files_skipped = %s, files_failed = %s, error_message = %s,
                   completed_at = NOW()
                   WHERE run_id = %s""",
                (status, files_found, files_processed, files_skipped, files_failed, error_message, run_id)
            )

    # --- Ingested Files ---
    def register_file(self, run_id, file_path, source_type):
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        try:
            with self.get_cursor() as cur:
                cur.execute(
                    """INSERT INTO ingested_files (run_id, file_path, file_name, source_type, file_size_bytes)
                       VALUES (%s, %s, %s, %s, %s)
                       ON CONFLICT (file_path) DO NOTHING
                       RETURNING id""",
                    (run_id, file_path, file_name, source_type, file_size)
                )
                row = cur.fetchone()
                return row['id'] if row else None
        except Exception as e:
            print(f"Error registering file {file_path}: {e}")
            return None

    def update_file(self, file_id, status, wiki_pages_created=0, wiki_pages_updated=0, entities_extracted=0, concepts_extracted=0, error_message=None):
        with self.get_cursor() as cur:
            cur.execute(
                """UPDATE ingested_files SET 
                   status = %s, wiki_pages_created = %s, wiki_pages_updated = %s, 
                   entities_extracted = %s, concepts_extracted = %s, error_message = %s,
                   ingested_at = NOW()
                   WHERE id = %s""",
                (status, wiki_pages_created, wiki_pages_updated, entities_extracted, concepts_extracted, error_message, file_id)
            )

    # --- Pipeline Steps ---
    def start_step(self, run_id, step_name, file_id=None):
        with self.get_cursor() as cur:
            cur.execute(
                """INSERT INTO pipeline_steps (run_id, file_id, step_name)
                   VALUES (%s, %s, %s) RETURNING id""",
                (run_id, file_id, step_name)
            )
            return cur.fetchone()['id']

    def complete_step(self, step_id, status, output_summary=None, error_message=None):
        with self.get_cursor() as cur:
            # Calculate duration using started_at
            cur.execute(
                """UPDATE pipeline_steps SET 
                   status = %s, output_summary = %s, error_message = %s,
                   completed_at = NOW(),
                   duration_ms = EXTRACT(EPOCH FROM (NOW() - started_at)) * 1000
                   WHERE id = %s""",
                (status, output_summary, error_message, step_id)
            )

    # --- AI Calls ---
    def log_ai_call(self, run_id, step_name, model, operation, input_tokens, output_tokens, duration_ms, success=True, file_id=None, error_message=None):
        cost = estimate_cost(model, input_tokens, output_tokens)
        with self.get_cursor() as cur:
            cur.execute(
                """INSERT INTO ai_calls (run_id, file_id, step_name, model, operation, input_tokens, output_tokens, estimated_cost_usd, duration_ms, success, error_message)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (run_id, file_id, step_name, model, operation, input_tokens, output_tokens, cost, duration_ms, success, error_message)
            )

    def write_ai_summary(self, run_id):
        with self.get_cursor() as cur:
            cur.execute(
                """INSERT INTO ai_call_summary (run_id, total_calls, pro_calls, flash_calls, total_input_tokens, total_output_tokens, total_tokens, estimated_cost_usd)
                   SELECT 
                       run_id,
                       COUNT(*),
                       COUNT(*) FILTER (WHERE model LIKE '%%pro%%'),
                       COUNT(*) FILTER (WHERE model LIKE '%%flash%%'),
                       SUM(input_tokens),
                       SUM(output_tokens),
                       SUM(total_tokens),
                       SUM(estimated_cost_usd)
                   FROM ai_calls
                   WHERE run_id = %s
                   GROUP BY run_id
                   ON CONFLICT (run_id) DO UPDATE SET
                       total_calls = EXCLUDED.total_calls,
                       pro_calls = EXCLUDED.pro_calls,
                       flash_calls = EXCLUDED.flash_calls,
                       total_input_tokens = EXCLUDED.total_input_tokens,
                       total_output_tokens = EXCLUDED.total_output_tokens,
                       total_tokens = EXCLUDED.total_tokens,
                       estimated_cost_usd = EXCLUDED.estimated_cost_usd,
                       generated_at = NOW()""",
                (run_id,)
            )

# Singleton instance
db = Database()
