from app import approvals
from app.runtime_context import set_current_session_id
from app.tools import workspace_tools


def _action_id_from_pending_response(response: str) -> str:
    for line in response.splitlines():
        if line.startswith("action_id="):
            return line.split("=", 1)[1].strip()
    raise AssertionError(f"action_id not found in response: {response}")


def _configure_isolated_workspace(tmp_path, monkeypatch):
    workspace_root = tmp_path / "workspace"
    state_dir = tmp_path / "state"
    workspace_root.mkdir()

    monkeypatch.setattr(workspace_tools, "WORKSPACE_ROOT", workspace_root)
    monkeypatch.setattr(approvals, "STATE_DIR", state_dir)
    monkeypatch.setattr(approvals, "PENDING_ACTIONS_FILE", state_dir / "pending_actions.json")
    set_current_session_id("test-session")

    return workspace_root


def test_request_batch_operations_accepts_create_directory(tmp_path, monkeypatch):
    _configure_isolated_workspace(tmp_path, monkeypatch)

    response = workspace_tools.request_batch_operations(
        [{"type": "create_directory", "path": "empty-dir"}]
    )

    assert response.startswith("__PENDING_APPROVAL__")
    pending = approvals.list_pending_actions()
    assert len(pending) == 1
    assert pending[0]["action_type"] == "batch_operations"
    assert pending[0]["payload"]["operations"] == [
        {"type": "create_directory", "path": "empty-dir"}
    ]
    assert "create_directory(empty-dir)" in pending[0]["summary"]


def test_execute_batch_create_directory_creates_directory(tmp_path, monkeypatch):
    workspace_root = _configure_isolated_workspace(tmp_path, monkeypatch)
    response = workspace_tools.request_batch_operations(
        [{"type": "create_directory", "path": "empty-dir"}]
    )

    result = workspace_tools.execute_pending_action(_action_id_from_pending_response(response))

    assert "실행 완료" in result
    assert (workspace_root / "empty-dir").is_dir()


def test_execute_batch_create_directory_creates_nested_path(tmp_path, monkeypatch):
    workspace_root = _configure_isolated_workspace(tmp_path, monkeypatch)
    response = workspace_tools.request_batch_operations(
        [{"type": "create_directory", "path": "nested/child", "create_parents": True}]
    )

    result = workspace_tools.execute_pending_action(_action_id_from_pending_response(response))

    assert "실행 완료" in result
    assert (workspace_root / "nested" / "child").is_dir()


def test_execute_batch_create_directory_fails_for_existing_directory(tmp_path, monkeypatch):
    workspace_root = _configure_isolated_workspace(tmp_path, monkeypatch)
    (workspace_root / "exists").mkdir()
    response = workspace_tools.request_batch_operations(
        [{"type": "create_directory", "path": "exists"}]
    )
    action_id = _action_id_from_pending_response(response)

    result = workspace_tools.execute_pending_action(action_id)

    assert "실행 실패" in result
    assert "디렉터리가 이미 존재합니다" in result
    assert approvals.get_action(action_id)["status"] == "failed"


def test_execute_batch_create_directory_fails_for_existing_file(tmp_path, monkeypatch):
    workspace_root = _configure_isolated_workspace(tmp_path, monkeypatch)
    (workspace_root / "exists.txt").write_text("already here", encoding="utf-8")
    response = workspace_tools.request_batch_operations(
        [{"type": "create_directory", "path": "exists.txt"}]
    )
    action_id = _action_id_from_pending_response(response)

    result = workspace_tools.execute_pending_action(action_id)

    assert "실행 실패" in result
    assert "파일이 이미 존재합니다" in result
    assert approvals.get_action(action_id)["status"] == "failed"


def test_existing_batch_create_file_still_works(tmp_path, monkeypatch):
    workspace_root = _configure_isolated_workspace(tmp_path, monkeypatch)
    response = workspace_tools.request_batch_operations(
        [{"type": "create_file", "path": "still-works.txt"}]
    )

    result = workspace_tools.execute_pending_action(_action_id_from_pending_response(response))

    assert "실행 완료" in result
    assert (workspace_root / "still-works.txt").is_file()


def test_batch_can_mix_create_directory_and_write_file(tmp_path, monkeypatch):
    workspace_root = _configure_isolated_workspace(tmp_path, monkeypatch)
    response = workspace_tools.request_batch_operations(
        [
            {"type": "create_directory", "path": "mixed"},
            {
                "type": "write_file",
                "path": "mixed/readme.md",
                "content": "hello",
                "mode": "create_only",
            },
        ]
    )

    result = workspace_tools.execute_pending_action(_action_id_from_pending_response(response))

    assert "실행 완료" in result
    assert (workspace_root / "mixed").is_dir()
    assert (workspace_root / "mixed" / "readme.md").read_text(encoding="utf-8") == "hello"
