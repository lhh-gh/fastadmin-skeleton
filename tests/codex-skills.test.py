"""Run with: python -B tests/codex-skills.test.py (no database writes)."""

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch


SKILLS = Path(__file__).resolve().parents[1] / ".agents" / "skills"
spec = importlib.util.spec_from_file_location(
    "mysql_dev_db", SKILLS / "mysql-dev-db" / "scripts" / "mysql_dev_db.py"
)
db = importlib.util.module_from_spec(spec)
spec.loader.exec_module(db)


class CodexSkillsTest(unittest.TestCase):
    def test_references_resolve_inside_each_skill(self):
        for skill in (SKILLS / "fastadmin", SKILLS / "mysql-dev-db"):
            for document in skill.rglob("*.md"):
                for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
                    if "://" in link or link.startswith("#"):
                        continue
                    target = (document.parent / link.split("#", 1)[0]).resolve()
                    self.assertTrue(target.is_relative_to(skill.resolve()), link)
                    self.assertTrue(target.is_file(), link)

    @patch.dict(os.environ, {}, clear=True)
    def test_env_overrides_use_source_priority_and_allow_empty_password(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".env").write_text(
                "MYSQL_HOST=127.0.0.1\nDB_USERNAME=dev\nDB_DATABASE=base\nDB_PASSWORD=base-secret\n",
                encoding="utf-8",
            )
            (root / ".env.local").write_text(
                "DB_HOST=localhost\nDB_DATABASE=local\nDB_PASSWORD=\n", encoding="utf-8"
            )
            cfg, _ = db.load_config(root)
            self.assertEqual(cfg["host"], "localhost")
            self.assertEqual(cfg["database"], "local")
            self.assertEqual(cfg["password"], "")

    @patch.dict(os.environ, {}, clear=True)
    def test_ai_config_is_a_working_fallback(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".ai").mkdir()
            (root / ".ai" / "config.json").write_text(
                json.dumps({"mysql_dev_db": {"user": "dev", "database": "local", "port": 3307}}),
                encoding="utf-8",
            )
            cfg, _ = db.load_config(root)
            self.assertEqual(cfg["user"], "dev")
            self.assertEqual(cfg["database"], "local")
            self.assertEqual(cfg["port"], "3307")

    @patch.dict(os.environ, {
        "MYSQL_HOST": "127.0.0.2", "MYSQL_USER": "environment-user",
        "MYSQL_DATABASE": "environment-db", "MYSQL_PASSWORD": "environment-secret",
    }, clear=True)
    def test_partial_ai_config_does_not_mask_environment_fallbacks(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".ai").mkdir()
            (root / ".ai" / "config.json").write_text(
                json.dumps({"mysql_dev_db": {"user": "dev", "password": ""}}),
                encoding="utf-8",
            )
            cfg, _ = db.load_config(root)
            self.assertEqual(cfg["host"], "127.0.0.2")
            self.assertEqual(cfg["user"], "dev")
            self.assertEqual(cfg["database"], "environment-db")
            self.assertEqual(cfg["password"], "")

    @patch.dict(os.environ, {}, clear=True)
    def test_invalid_ai_config_reports_the_file_instead_of_using_another_database(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".ai").mkdir()
            config_path = root / ".ai" / "config.json"
            for content in ('{"secret": "do-not-print",', '[]', '{"mysql_dev_db": []}'):
                with self.subTest(content=content):
                    config_path.write_text(content, encoding="utf-8")
                    with self.assertRaises(SystemExit) as error:
                        db.load_config(root)
                    self.assertIn(str(config_path), str(error.exception))
                    self.assertNotIn("do-not-print", str(error.exception))

    @patch.dict(os.environ, {"USERNAME": "windows-user", "HOSTNAME": "system-host"}, clear=True)
    def test_operating_system_identity_is_not_a_database_account(self):
        with tempfile.TemporaryDirectory() as temporary:
            cfg, _ = db.load_config(Path(temporary))
            self.assertEqual(cfg["user"], "")
            self.assertEqual(cfg["host"], "127.0.0.1")

    @patch.dict(os.environ, {"DATABASE_URL": "mysql://other:secret@remote/other"}, clear=True)
    def test_environment_url_does_not_override_project_config(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".env").write_text(
                "[DATABASE]\nHOSTNAME=127.0.0.1\nUSERNAME=dev\nDATABASE=local\nPASSWORD=\"local # secret\"\n",
                encoding="utf-8",
            )
            cfg, _ = db.load_config(root)
            self.assertEqual(cfg["host"], "127.0.0.1")
            self.assertEqual(cfg["user"], "dev")
            self.assertEqual(cfg["database"], "local")
            self.assertEqual(cfg["password"], "local # secret")

    @patch.dict(os.environ, {"MYSQL_PWD": "inherited-secret"}, clear=True)
    def test_cli_password_is_not_in_arguments_or_inherited(self):
        cfg = {"host": "127.0.0.1", "port": "3306", "user": "dev", "database": "local", "charset": "utf8mb4", "password": ""}
        with patch.object(db, "find_mysql_bin", return_value="mysql"), patch.object(db.subprocess, "run") as run:
            run.return_value.returncode = 0
            self.assertEqual(db.run_mysql(cfg, sql="SELECT 1"), 0)
            self.assertEqual(run.call_args.kwargs["env"]["MYSQL_PWD"], "")
            self.assertNotIn("inherited-secret", " ".join(run.call_args.args[0]))

    @patch.dict(os.environ, {}, clear=True)
    def test_sql_file_never_falls_back_to_a_string_splitter(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".env").write_text("DB_USERNAME=dev\nDB_DATABASE=local\n", encoding="utf-8")
            sql_file = root / "change.sql"
            sql_file.write_text("INSERT INTO sample VALUES ('a;\nb');\n", encoding="utf-8")
            arguments = ["mysql_dev_db.py", "--project", str(root), "file", str(sql_file)]
            with patch.object(sys, "argv", arguments), patch.object(db, "find_mysql_bin", return_value=None), patch.object(db, "run_pymysql") as fallback, contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(db.main(), 127)
                fallback.assert_not_called()


if __name__ == "__main__":
    unittest.main()
