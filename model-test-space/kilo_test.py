from openai import OpenAI
import os

MODEL_ID = "kilo-auto/free"

client = OpenAI(
    api_key=os.environ["KILOCODE_API_KEY"],
    base_url="https://api.kilo.ai/api/gateway",
)
while True:
    prompt = input("질문을 입력하세요: ")    
    resp = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {"role": "user", "content": prompt}
        ],
        # max_tokens=200,
    )
    print(resp.choices[0].message.content)
