from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _frontend_dir() -> Path:
    return _project_root() / "frontend"


def _frontend_dist_dir() -> Path:
    return _frontend_dir() / "dist"


def _run_subprocess(cmd: list[str], cwd: Path | None = None) -> int:
    return subprocess.call(cmd, cwd=str(cwd) if cwd else None)


def _spawn_subprocess(cmd: list[str], cwd: Path | None = None) -> subprocess.Popen:
    return subprocess.Popen(
        cmd,
        cwd=str(cwd) if cwd else None,
    )


def _frontend_dev_url(frontend_host: str, frontend_port: int) -> str:
    host = frontend_host.strip() or "localhost"

    # 브라우저 오픈은 localhost 쪽이 더 안정적
    if host in {"127.0.0.1", "0.0.0.0", "::"}:
        host = "localhost"

    return f"http://{host}:{frontend_port}"


def _terminate_process(proc: subprocess.Popen | None) -> None:
    if proc is None:
        return

    if proc.poll() is not None:
        return

    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def cmd_doctor() -> int:
    from app.paths import (
        OUROBOROS_HOME,
        STATE_DIR,
        LOGS_DIR,
        NOTES_DIR,
        WORKSPACE_ROOT,
    )

    print("Ouroboros Doctor")
    print("-" * 40)
    print(f"OUROBOROS_HOME = {OUROBOROS_HOME}")
    print(f"STATE_DIR      = {STATE_DIR}")
    print(f"LOGS_DIR       = {LOGS_DIR}")
    print(f"NOTES_DIR      = {NOTES_DIR}")
    print(f"WORKSPACE_ROOT = {WORKSPACE_ROOT}")
    print("-" * 40)
    print(f"Python         = {sys.executable}")
    print(f"Project root   = {_project_root()}")
    print(f"Frontend dir   = {_frontend_dir()}")
    print(f"Frontend dist  = {_frontend_dist_dir()}")
    return 0


def cmd_tui() -> int:
    return _run_subprocess([sys.executable, "-m", "app.main"])


def cmd_api(host: str, port: int, reload: bool) -> int:
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.api.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]

    if reload:
        cmd.append("--reload")

    return _run_subprocess(cmd)


def cmd_frontend_build() -> int:
    frontend_dir = _frontend_dir()
    if not frontend_dir.exists():
        print(f"[ERROR] frontend 디렉터리를 찾지 못했습니다: {frontend_dir}")
        return 1

    build_cmd_text = os.getenv("OUROBOROS_FRONTEND_BUILD_CMD", "npm run build")
    build_cmd = shlex.split(build_cmd_text)

    print(f"[INFO] frontend build: {' '.join(build_cmd)}")
    print(f"[INFO] frontend cwd: {frontend_dir}")

    return _run_subprocess(build_cmd, cwd=frontend_dir)


def cmd_web(
    host: str,
    port: int,
    reload: bool,
    dev: bool,
    frontend_host: str,
    frontend_port: int,
    open_browser: bool,
    build: bool,
) -> int:
    frontend_dir = _frontend_dir()
    frontend_dist_dir = _frontend_dist_dir()

    if dev:
        if not frontend_dir.exists():
            print(f"[ERROR] frontend 디렉터리를 찾지 못했습니다: {frontend_dir}")
            return 1

        backend_cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "app.api.main:app",
            "--host",
            host,
            "--port",
            str(port),
        ]
        if reload:
            backend_cmd.append("--reload")

        frontend_cmd_text = os.getenv(
            "OUROBOROS_FRONTEND_DEV_CMD",
            f"npm run dev -- --host {frontend_host} --port {frontend_port}",
        )
        frontend_cmd = shlex.split(frontend_cmd_text)

        print("[INFO] dev 모드로 실행합니다.")
        print(f"[INFO] backend: {' '.join(backend_cmd)}")
        print(f"[INFO] frontend: {' '.join(frontend_cmd)}")
        print(f"[INFO] frontend cwd: {frontend_dir}")

        backend_proc: subprocess.Popen | None = None
        frontend_proc: subprocess.Popen | None = None

        try:
            backend_proc = _spawn_subprocess(backend_cmd)
            frontend_proc = _spawn_subprocess(frontend_cmd, cwd=frontend_dir)

            if open_browser:
                time.sleep(2.5)
                webbrowser.open(_frontend_dev_url(frontend_host, frontend_port))

            backend_return = backend_proc.wait()
            return backend_return
        except KeyboardInterrupt:
            print("\n[INFO] 종료 요청을 받았습니다.")
            return 0
        finally:
            _terminate_process(frontend_proc)
            _terminate_process(backend_proc)

    # 일반 모드: dist가 없거나 --build면 자동 빌드
    if build or not frontend_dist_dir.exists():
        build_result = cmd_frontend_build()
        if build_result != 0:
            return build_result

    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.api.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    if reload:
        backend_cmd.append("--reload")

    print("[INFO] 일반 web 모드로 실행합니다.")
    print(f"[INFO] backend: {' '.join(backend_cmd)}")
    print(f"[INFO] serving dist: {frontend_dist_dir}")

    backend_proc: subprocess.Popen | None = None

    try:
        backend_proc = _spawn_subprocess(backend_cmd)

        if open_browser:
            time.sleep(1.5)
            webbrowser.open(f"http://{host}:{port}")

        return backend_proc.wait()
    except KeyboardInterrupt:
        print("\n[INFO] 종료 요청을 받았습니다.")
        return 0
    finally:
        _terminate_process(backend_proc)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ouroboros",
        description="Ouroboros agent launcher",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="현재 경로/설정 상태 점검")
    subparsers.add_parser("tui", help="기존 CLI/TUI 실행")

    api_parser = subparsers.add_parser("api", help="FastAPI 서버 실행")
    api_parser.add_argument("--host", default="127.0.0.1")
    api_parser.add_argument("--port", type=int, default=8000)
    api_parser.add_argument("--reload", action="store_true")

    web_parser = subparsers.add_parser("web", help="웹 실행용 서버 시작")
    web_parser.add_argument("--host", default="127.0.0.1")
    web_parser.add_argument("--port", type=int, default=8000)
    web_parser.add_argument("--reload", action="store_true")
    web_parser.add_argument("--dev", action="store_true")
    web_parser.add_argument("--build", action="store_true")
    web_parser.add_argument("--frontend-port", type=int, default=5173)
    web_parser.add_argument("--no-open", action="store_true")
    web_parser.add_argument("--frontend-host", default="localhost")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "doctor":
        return cmd_doctor()

    if args.command == "tui":
        return cmd_tui()

    if args.command == "api":
        return cmd_api(
            host=args.host,
            port=args.port,
            reload=args.reload,
        )

    if args.command == "web":
        return cmd_web(
            host=args.host,
            port=args.port,
            reload=args.reload,
            dev=args.dev,
            build=args.build,
            frontend_host=args.frontend_host,
            frontend_port=args.frontend_port,
            open_browser=not args.no_open,
        )

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())