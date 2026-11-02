"""Tests never load a workstation .env, connect to a database, or use network APIs."""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest
import psycopg2
import dotenv

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[1] / 'scripts')]
os.environ['POSTGRES_URL'] = 'postgresql://unit-test-only'
dotenv.load_dotenv = MagicMock(return_value=False)
psycopg2.connect = MagicMock()


@pytest.fixture(autouse=True)
def isolated_environment(tmp_path, monkeypatch):
    import socket
    (tmp_path / 'raw/youtube').mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    def denied(*args, **kwargs):
        raise RuntimeError('Network disabled during tests')
    monkeypatch.setattr(socket.socket, 'connect', denied)
