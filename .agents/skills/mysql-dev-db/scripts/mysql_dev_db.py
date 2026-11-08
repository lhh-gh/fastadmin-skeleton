#!/usr/bin/env python3
"""MySQL local-dev helper for repository-local Codex skills.

Reads database config from project .env files, .ai/config.json, and environment
variables. Uses mysql CLI first, then PyMySQL as a fallback.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


ENV_FILES = (".env", ".env.local", ".env.development")
CONFIG_KEYS = {
    "host": [
        "MYSQL_HOST",
        "DB_HOST",
        "DATABASE_HOST",
        "database.hostname",
        "DATABASE.HOSTNAME",
        "HOSTNAME",
    ],
    "port": [
        "MYSQL_PORT",
        "DB_PORT",
        "DATABASE_PORT",
        "database.hostport",
        "DATABASE.HOSTPORT",
        "HOSTPORT",
    ],
    "user": [
        "MYSQL_USER",
        "DB_USER",
        "DB_USERNAME",
        "DATABASE_USER",
        "database.username",
        "DATABASE.USERNAME",
        "USERNAME",
    ],
    "password": [
        "MYSQL_PASSWORD",
        "DB_PASSWORD",
        "DATABASE_PASSWORD",
        "database.password",
        "DATABASE.PASSWORD",
        "PASSWORD",
    ],
    "database": [
        "MYSQL_DATABASE",
        "DB_DATABASE",
        "DB_NAME",
        "DATABASE_NAME",
        "database.database",
        "DATABASE.DATABASE",
        "DATABASE",
    ],
    "charset": [
        "MYSQL_CHARSET",
        "DB_CHARSET",
        "DATABASE_CHARSET",
        "database.charset",
        "DATABASE.CHARSET",
        "CHARSET",
    ],
}


def project_root(start: Path) -> Path:
    current = start.resolve()
    markers = (".env", ".ai", ".git", "composer.json", "package.json", "think")
    for path in (current, *current.parents):
        if any((path / marker).exists() for marker in markers):
            return path
    return current


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_env_file(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    section = ""
    if not path.exists():
        return data

    for raw_line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            continue
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value[:1] not in {"'", '"'}:
            value = value.split(" #", 1)[0].strip()
        value = strip_quotes(value)
        data[key] = value
        if section:
            data[f"{section}.{key}"] = value
            data[f"{section.upper()}.{key.upper()}"] = value
        if "." in key:
            data[key.upper()] = value
    return data


def load_ai_config(root: Path) -> dict[str, str]:
    config_path = root / ".ai" / "config.json"
    if not config_path.exists():
        return {}
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise SystemExit(f"Cannot read database configuration: {config_path}") from None
    if not isinstance(raw, dict):
        raise SystemExit(f"Configuration must contain a JSON object: {config_path}")
    if "mysql_dev_db" not in raw:
        return {}
    cfg = raw["mysql_dev_db"]
    if not isinstance(cfg, dict):
        raise SystemExit(f"mysql_dev_db must be a JSON object: {config_path}")
    return {
        key: str(value) for key, value in cfg.items()
        if key in CONFIG_KEYS and value is not None
    }


def parse_database_url(value: str) -> dict[str, str]:
    if not value:
        return {}
    parsed = urlparse(value)
    if parsed.scheme not in {"mysql", "mysql+pymysql", "mariadb"}:
        return {}
    return {
        "host": parsed.hostname or "",
        "port": str(parsed.port or ""),
        "user": unquote(parsed.username or ""),
        "password": unquote(parsed.password or ""),
        "database": (parsed.path or "").lstrip("/"),
    }


def first_value(sources: list[dict[str, str]], names: list[str]) -> str | None:
    for source in sources:
        for name in names:
            value = source.get(name)
            if value is not None:
                return str(value)
    return None


def load_config(root: Path) -> tuple[dict[str, str], list[str]]:
    raw_sources = [(name, parse_env_file(root / name)) for name in reversed(ENV_FILES)]
    raw_sources.append((".ai/config.json", load_ai_config(root)))
    raw_sources.append(("environment", {
        key: value for key, value in os.environ.items()
        if key.startswith(("MYSQL_", "DB_", "DATABASE_"))
    }))
    sources = []
    ordered_sources = []
    for name, source in raw_sources:
        values = {
            key: first_value([source], [key, *aliases])
            for key, aliases in CONFIG_KEYS.items()
        }
        normalized = parse_database_url(source.get("DATABASE_URL", ""))
        normalized.update({key: value for key, value in values.items() if value is not None})
        if normalized:
            sources.append(name)
            ordered_sources.append(normalized)

    cfg = {
        key: first_value(ordered_sources, [key]) or ""
        for key in CONFIG_KEYS
    }

    cfg["host"] = cfg.get("host") or "127.0.0.1"
    cfg["port"] = str(cfg.get("port") or "3306")
    cfg["charset"] = cfg.get("charset") or "utf8mb4"
    return cfg, sources


def find_mysql_bin() -> str | None:
    env_bin = os.environ.get("MYSQL_BIN")
    if env_bin and Path(env_bin).is_file():
        return env_bin
    return shutil.which("mysql")


def mysql_args(cfg: dict[str, str], include_db: bool = True) -> list[str]:
    args = [
        "--protocol=TCP",
        "-h",
        cfg["host"],
        "-P",
        str(cfg["port"]),
        "-u",
        cfg["user"],
        f"--default-character-set={cfg['charset']}",
        "--batch",
        "--raw",
    ]
    if include_db and cfg.get("database"):
        args += ["--database", cfg["database"]]
    return args


def run_mysql(cfg: dict[str, str], sql: str | None = None, sql_file: Path | None = None) -> int:
    mysql_bin = find_mysql_bin()
    if not mysql_bin:
        return 127
    env = os.environ.copy()
    env["MYSQL_PWD"] = cfg.get("password") or ""
    args = [mysql_bin, *mysql_args(cfg)]
    if sql is not None:
        args += ["-e", sql]
        proc = subprocess.run(args, env=env, text=True, encoding="utf-8", errors="replace")
    elif sql_file is not None:
        with sql_file.open("r", encoding="utf-8-sig", errors="replace") as stream:
            proc = subprocess.run(args, env=env, stdin=stream, text=True, encoding="utf-8", errors="replace")
    else:
        proc = subprocess.run(args, env=env, text=True, encoding="utf-8", errors="replace")
    return proc.returncode


def pymysql_connect(cfg: dict[str, str]):
    try:
        import pymysql  # type: ignore
    except ImportError:
        return None
    return pymysql.connect(
        host=cfg["host"],
        port=int(cfg["port"]),
        user=cfg["user"],
        password=cfg.get("password") or "",
        database=cfg.get("database") or None,
        charset=cfg.get("charset") or "utf8mb4",
        autocommit=True,
    )


def print_rows(cursor) -> None:
    columns = [item[0] for item in cursor.description or []]
    if columns:
        print("\t".join(columns))
    for row in cursor.fetchall():
        print("\t".join("" if value is None else str(value) for value in row))


def run_pymysql(cfg: dict[str, str], sql: str) -> int:
    conn = pymysql_connect(cfg)
    if conn is None:
        print("Neither mysql CLI nor pymysql is available.", file=sys.stderr)
        print("Install fallback with: pip install --user pymysql", file=sys.stderr)
        return 127
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            if cursor.description:
                print_rows(cursor)
    return 0


def require_config(cfg: dict[str, str]) -> bool:
    missing = [key for key in ("host", "port", "user", "database") if not cfg.get(key)]
    if missing:
        print("Missing database config: " + ", ".join(missing), file=sys.stderr)
        return False
    return True


def mask(value: str) -> str:
    if not value:
        return ""
    return "***"


def command_sql(command: str, extra: list[str]) -> str:
    if command == "ping":
        return "SELECT 1 AS ok"
    if command == "tables":
        return "SHOW TABLES"
    if command == "schema":
        return (
            "SELECT TABLE_NAME, TABLE_ROWS, ENGINE, TABLE_COLLATION "
            "FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA = DATABASE() ORDER BY TABLE_NAME"
        )
    if command == "describe":
        if not extra:
            raise SystemExit("describe requires a table name")
        table = extra[0].replace("`", "``")
        return f"DESCRIBE `{table}`"
    if command == "query":
        if not extra:
            raise SystemExit("query requires SQL text")
        return " ".join(extra)
    raise SystemExit(f"Unsupported command: {command}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Local MySQL helper for Codex")
    parser.add_argument("command", choices=["config", "ping", "tables", "schema", "describe", "query", "file"])
    parser.add_argument("args", nargs="*")
    parser.add_argument("--project", default=".", help="Project root or any path inside the project")
    parser.add_argument("--no-cli", action="store_true", help="Skip mysql CLI and use PyMySQL fallback directly")
    parsed = parser.parse_args()

    root = project_root(Path(parsed.project))
    cfg, sources = load_config(root)

    if parsed.command == "config":
        print(json.dumps({
            "project_root": str(root),
            "sources": sources,
            "host": cfg.get("host", ""),
            "port": cfg.get("port", ""),
            "user": cfg.get("user", ""),
            "password": mask(cfg.get("password", "")),
            "database": cfg.get("database", ""),
            "charset": cfg.get("charset", ""),
            "mysql_cli": find_mysql_bin() or "",
        }, ensure_ascii=False, indent=2))
        return 0

    if not require_config(cfg):
        return 2

    if parsed.command == "file":
        if not parsed.args:
            print("file requires a SQL file path", file=sys.stderr)
            return 2
        sql_file = (Path.cwd() / parsed.args[0]).resolve()
        if not sql_file.exists():
            print(f"SQL file not found: {sql_file}", file=sys.stderr)
            return 2
        if not parsed.no_cli:
            rc = run_mysql(cfg, sql_file=sql_file)
            if rc != 127:
                return rc
        print("SQL files require mysql CLI. Set MYSQL_BIN or add mysql to PATH.", file=sys.stderr)
        return 127

    sql = command_sql(parsed.command, parsed.args)
    if not parsed.no_cli:
        rc = run_mysql(cfg, sql=sql)
        if rc != 127:
            return rc
    return run_pymysql(cfg, sql)


if __name__ == "__main__":
    raise SystemExit(main())
