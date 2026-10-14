"""Run the backend test suite against a throwaway local Postgres (the database used on Vercel).

    pip install pgserver "psycopg[binary]"
    python tests/run_pg.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

import pgserver

here = os.path.dirname(os.path.abspath(__file__))
data = tempfile.mkdtemp(prefix="dicts-pg-")
srv = pgserver.get_server(data, cleanup_mode="stop")
try:
    env = dict(os.environ, TEST_DATABASE_URL=srv.get_uri())
    code = subprocess.call([sys.executable, "-m", "pytest", "-q", os.path.join(here, "test_api.py")] + sys.argv[1:], env=env)
finally:
    srv.cleanup()
    shutil.rmtree(data, ignore_errors=True)
sys.exit(code)
