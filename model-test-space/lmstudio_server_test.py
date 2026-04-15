import os
from openai import OpenAI

# LM Studio 서버 주소 설정
client = OpenAI(
    base_url=os.environ["LM_STUDIO_BASE_URL"],
    api_key="lm-studio"  # 인증 안 쓰면 보통 아무 문자열이나 넣어도 됨
)

response = client.chat.completions.create(
    model="google/gemma-4-e4b",
    # model="liquid-lfm2.5-1.2b:2",
    messages=[
        {"role": "system", "content": "너는 친절한 한국어 도우미다."},
        {"role": "user", "content": "파이썬이 왜 데이터 분석에 많이 쓰이는지 짧게 설명해줘."}
    ],
    temperature=0.0,
)

print(response.choices[0].message.content)