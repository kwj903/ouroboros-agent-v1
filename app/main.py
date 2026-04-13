from __future__ import annotations

from app.agent import run_agent
from app.approvals import get_action
from app.conversation_state import (
    SessionState,
    create_new_session,
    delete_session_choice,
    format_session_list,
    rename_session_choice,
    resolve_session_choice,
)
from app.memory_manager import (
    RECENT_HISTORY_LIMIT,
    build_memory_context,
    compact_history_if_needed,
    update_workspace_state_from_approval,
    update_workspace_state_from_trace,
)
from app.runtime_context import set_current_session_id
from app.settings import DEFAULT_OUTPUT_MODE, DEFAULT_RESPONSE_LANGUAGE
from app.tools.workspace_tools import (
    execute_pending_action,
    format_pending_actions,
    reject_pending_action,
)
from app.long_term_memory import (
    accept_memory_suggestion,
    add_memory_note,
    dismiss_memory_suggestion,
    format_memory_records,
    format_memory_suggestions,
    generate_memory_suggestions,
    list_memory_suggestions,
    list_recent_memory_notes,
    search_memory_records,
    update_memory_note,
    delete_memory_note,
)


def _extract_action_id_from_answer(answer: str) -> str | None:
    for line in answer.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("action_id:"):
            return stripped.split(":", 1)[1].strip()
    return None


def _ask_approval_and_execute(action_id: str) -> str:
    while True:
        choice = input("\n이 작업을 실행할까요? (y/n) > ").strip().lower()

        if choice in {"y", "yes"}:
            return execute_pending_action(action_id)

        if choice in {"n", "no"}:
            return reject_pending_action(action_id)

        print("y 또는 n으로 입력해주세요.")
        
        
def _ask_yes_no(prompt: str) -> bool:
    while True:
        choice = input(f"\n{prompt} (y/n) > ").strip().lower()

        if choice in {"y", "yes"}:
            return True

        if choice in {"n", "no"}:
            return False

        print("y 또는 n으로 입력해주세요.")


def _get_session_for_action(action_id: str, fallback: SessionState) -> SessionState:
    action = get_action(action_id)
    if action is None:
        return fallback

    session_id = action.get("session_id")
    if not session_id:
        return fallback

    return SessionState(session_id=session_id)


def _handle_local_command(
    user_input: str,
    session_state: SessionState,
) -> tuple[str | None, SessionState]:
    stripped = user_input.strip()
    if not stripped:
        return None, session_state

    parts = stripped.split(maxsplit=1)
    command = parts[0].lower()

    if command in {"pending", "대기"}:
        return format_pending_actions(), session_state

    if command == "memories":
        recent = list_recent_memory_notes(limit=10)
        return format_memory_records(recent), session_state

    if command == "remember":
        if len(parts) != 2 or not parts[1].strip():
            return "사용법: remember <기억할 내용>", session_state

        record = add_memory_note(
            content=parts[1].strip(),
            tags=["manual"],
            importance=4,
            note_type="general",
            source_session_id=session_state.session_id,
        )
        return (
            f"장기 기억 저장 완료\n"
            f"memory_id: {record['memory_id']}\n"
            f"content: {record['content']}",
            session_state,
        )

    if command == "search_memory":
        if len(parts) != 2 or not parts[1].strip():
            return "사용법: search_memory <검색어>", session_state

        results = search_memory_records(parts[1].strip(), max_results=5)
        if not results:
            return "관련 장기 기억이 없습니다.", session_state
        return format_memory_records(results), session_state

    if command == "forget":
        if len(parts) != 2 or not parts[1].strip():
            return "사용법: forget <memory_id>", session_state

        deleted = delete_memory_note(parts[1].strip())
        if not deleted:
            return "해당 memory_id를 찾지 못했습니다.", session_state

        return f"장기 기억 삭제 완료: {parts[1].strip()}", session_state

    if command == "update_memory":
        if len(parts) != 2 or not parts[1].strip():
            return "사용법: update_memory <memory_id> <새 내용>", session_state

        rest = parts[1].strip()
        subparts = rest.split(maxsplit=1)
        if len(subparts) != 2:
            return "사용법: update_memory <memory_id> <새 내용>", session_state

        memory_id, new_content = subparts[0], subparts[1].strip()

        try:
            updated = update_memory_note(
                memory_id=memory_id,
                new_content=new_content,
            )
        except ValueError as e:
            return f"장기 기억 수정 실패: {e}", session_state

        if updated is None:
            return "해당 memory_id를 찾지 못했습니다.", session_state

        return (
            f"장기 기억 수정 완료\n"
            f"id: {updated['memory_id']}\n"
            f"content: {updated['content']}",
            session_state,
        )

    if command == "memory_suggestions":
        items = list_memory_suggestions()
        return format_memory_suggestions(items), session_state

    if command == "save_suggestion":
        if len(parts) != 2 or not parts[1].strip():
            return "사용법: save_suggestion <번호|suggestion_id>", session_state

        record = accept_memory_suggestion(parts[1].strip())
        if record is None:
            return "해당 제안 후보를 찾지 못했습니다.", session_state

        return (
            f"기억 후보 저장 완료\n"
            f"memory_id: {record['memory_id']}\n"
            f"content: {record['content']}",
            session_state,
        )

    if command == "drop_suggestion":
        if len(parts) != 2 or not parts[1].strip():
            return "사용법: drop_suggestion <번호|suggestion_id>", session_state

        dropped = dismiss_memory_suggestion(parts[1].strip())
        if dropped is None:
            return "해당 제안 후보를 찾지 못했습니다.", session_state

        return (
            f"기억 후보 폐기 완료\n"
            f"suggestion_id: {dropped['suggestion_id']}\n"
            f"content: {dropped['content']}",
            session_state,
        )

    if command == "sessions":
        return format_session_list(current_session_id=session_state.session_id), session_state

    if command == "new":
        new_session = create_new_session()
        set_current_session_id(new_session.session_id)
        return (
            f"새 세션으로 전환했습니다: {new_session.session_id}",
            new_session,
        )

    if command == "title":
        if len(parts) != 2 or not parts[1].strip():
            return "사용법: title <새 이름>", session_state

        try:
            updated_title = session_state.set_title(parts[1].strip())
        except ValueError as e:
            return f"세션 이름 변경 실패: {e}", session_state

        return (
            f"현재 세션 이름 변경 완료: {session_state.session_id}\n"
            f"title: {updated_title}",
            session_state,
        )

    if command in {"rename_session", "session_rename", "ren_session"}:
        if len(parts) != 2 or not parts[1].strip():
            return (
                "사용법: rename_session <번호|session_id> <새 이름>",
                session_state,
            )

        rest = parts[1].strip()
        subparts = rest.split(maxsplit=1)
        if len(subparts) != 2:
            return (
                "사용법: rename_session <번호|session_id> <새 이름>",
                session_state,
            )

        target_choice, new_title = subparts[0], subparts[1].strip()
        if not new_title:
            return "새 이름이 비어 있습니다.", session_state

        updated_title = rename_session_choice(target_choice, new_title)
        if updated_title is None:
            return (
                "해당 세션을 찾지 못했거나 이름 변경에 실패했습니다.",
                session_state,
            )

        return (
            f"세션 이름 변경 완료\n"
            f"target: {target_choice}\n"
            f"title: {updated_title}",
            session_state,
        )

    if command in {"delete_session", "session_delete", "del_session"}:
        if len(parts) != 2 or not parts[1].strip():
            return "사용법: delete_session <번호> 또는 delete_session <session_id>", session_state

        target_choice = parts[1].strip()
        target_session_id = resolve_session_choice(target_choice)
        if target_session_id is None:
            return "해당 세션을 찾지 못했습니다. sessions 명령으로 목록을 확인하세요.", session_state

        confirmed = _ask_yes_no(
            f"세션을 삭제할까요?\n"
            f"session_id: {target_session_id}"
        )
        if not confirmed:
            return "세션 삭제를 취소했습니다.", session_state

        deleted_session_id = delete_session_choice(target_choice)
        if deleted_session_id is None:
            return "세션 삭제에 실패했습니다.", session_state

        # 현재 활성 세션을 삭제한 경우 새 세션 생성 후 자동 전환
        if deleted_session_id == session_state.session_id:
            new_session = create_new_session()
            set_current_session_id(new_session.session_id)
            return (
                f"현재 세션을 삭제했습니다: {deleted_session_id}\n"
                f"새 세션으로 전환했습니다: {new_session.session_id}",
                new_session,
            )

        return f"세션 삭제 완료: {deleted_session_id}", session_state

    if command == "switch":
        if len(parts) != 2 or not parts[1].strip():
            return "사용법: switch <번호> 또는 switch <session_id>", session_state

        target = resolve_session_choice(parts[1].strip())
        if target is None:
            return "해당 세션을 찾지 못했습니다. sessions 명령으로 목록을 확인하세요.", session_state

        switched = SessionState(session_id=target)
        set_current_session_id(switched.session_id)
        return f"세션 전환 완료: {switched.session_id}", switched

    if command in {"approve", "승인"}:
        if len(parts) != 2 or not parts[1].strip():
            return "사용법: approve <action_id>", session_state

        action_id = parts[1].strip()
        result = execute_pending_action(action_id)

        target_session = _get_session_for_action(action_id, session_state)
        target_session.append_history("assistant", f"승인 처리 결과: {result}")
        update_workspace_state_from_approval(target_session, action_id)
        compact_history_if_needed(target_session)

        return result, session_state

    if command in {"reject", "거부"}:
        if len(parts) != 2 or not parts[1].strip():
            return "사용법: reject <action_id>", session_state

        action_id = parts[1].strip()
        result = reject_pending_action(action_id)

        target_session = _get_session_for_action(action_id, session_state)
        target_session.append_history("assistant", f"승인 처리 결과: {result}")
        update_workspace_state_from_approval(target_session, action_id)
        compact_history_if_needed(target_session)

        return result, session_state

    return None, session_state


def main() -> None:
    print("Mini Agent CLI")
    print("종료하려면 exit 또는 quit 입력")
    print("세션 목록: sessions")
    print("세션 전환: switch <번호> 또는 switch <session_id>")
    print("새 세션: new")
    print("현재 세션 이름 변경: title <새 이름>")
    print("특정 세션 이름 변경: rename_session <번호|session_id> <새 이름>")
    print("세션 삭제: delete_session <번호> 또는 delete_session <session_id>")
    print("장기 기억 목록: memories")
    print("장기 기억 저장: remember <내용>")
    print("장기 기억 검색: search_memory <검색어>")
    print("장기 기억 삭제: forget <memory_id>")
    print("장기 기억 수정: update_memory <memory_id> <새 내용>")
    print("기억 후보 목록: memory_suggestions")
    print("기억 후보 저장: save_suggestion <번호|suggestion_id>")
    print("기억 후보 폐기: drop_suggestion <번호|suggestion_id>")
    print("승인 대기 보기: pending")
    print("작업 승인: approve <action_id>")
    print("작업 거부: reject <action_id>")
    print("-" * 40)

    debug_mode = True
    output_mode = DEFAULT_OUTPUT_MODE
    response_language = DEFAULT_RESPONSE_LANGUAGE

    session_state = create_new_session()
    set_current_session_id(session_state.session_id)
    print(f"현재 세션: {session_state.session_id}")

    while True:
        user_input = input("\n질문 > ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("종료합니다.")
            break

        if not user_input:
            continue

        local_command_result, session_state = _handle_local_command(
            user_input,
            session_state,
        )
        if local_command_result is not None:
            print(f"\n응답 > {local_command_result}")
            continue

        recent_history = session_state.get_recent_history(
            limit_messages=RECENT_HISTORY_LIMIT
        )
        memory_context = build_memory_context(
            session_state,
            user_input=user_input,
        )

        answer, trace_record = run_agent(
            user_input,
            debug=debug_mode,
            output_mode=output_mode,
            response_language=response_language,
            return_trace=True,
            chat_history=recent_history,
            memory_context=memory_context,
        )
        print(f"\n응답 > {answer}")

        session_state.append_history("user", user_input)
        session_state.append_history("assistant", answer)
        update_workspace_state_from_trace(session_state, trace_record)

        new_suggestions = generate_memory_suggestions(
            user_input=user_input,
            answer=answer,
            trace_record=trace_record,
            session_id=session_state.session_id,
        )

        if new_suggestions:
            print(
                f"\n[기억 후보 알림] 저장 후보 {len(new_suggestions)}건이 생겼습니다. "
                f"`memory_suggestions`로 확인하세요."
            )
        else:
            print(
                "\n[기억 후보 알림 없음] 새 후보가 생성되지 않았습니다. "
                "이미 저장된 기억과 중복되었거나 저장 가치가 낮을 수 있습니다."
            )

        action_id = _extract_action_id_from_answer(answer)
        if action_id:
            followup_result = _ask_approval_and_execute(action_id)
            print(f"\n승인 처리 결과 > {followup_result}")

            target_session = _get_session_for_action(action_id, session_state)
            target_session.append_history(
                "assistant",
                f"승인 처리 결과: {followup_result}",
            )
            update_workspace_state_from_approval(target_session, action_id)

        compact_history_if_needed(session_state)


if __name__ == "__main__":
    main()