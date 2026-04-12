from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)
while True:
    prompt = input("질문을 입력하세요: ")   
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    print(response.choices[0].message.content)
