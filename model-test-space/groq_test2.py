from openai import OpenAI
import os

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_API_KEY"],
)

while True:
    prompt = input("질문을 입력하세요: ")
    resp = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
    )
    print(resp.choices[0].message.content)