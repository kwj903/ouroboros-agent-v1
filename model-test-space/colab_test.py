import os
from remote_ollama import RemoteOllamaClient

llm = RemoteOllamaClient(
    base_url="https://ba48-34-127-13-88.ngrok-free.app",
    model=os.getenv("REMOTE_OLLAMA_MODEL", "gemma4:e4b"),
)

print(llm.health())

text = llm.generate("한국어로 한 문장만 답해. 너는 누구야?")
print(text)
while True:
    prompt = input("프롬프트: ").strip()

    if not prompt:
        print("빈 입력입니다.")
        continue

    if prompt.lower() in {"q", "quit", "exit"}:
        print("종료합니다.")
        break

    got_any = False
    for chunk in llm.stream(prompt):
        got_any = True
        print(chunk, end="", flush=True)

    print()

    if not got_any:
        print("[응답 없음]")