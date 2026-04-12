import os
from openrouter import OpenRouter

while True:
    prompt = input("질문을 입력하세요: ")
    with OpenRouter(api_key=os.getenv("OPENROUTER_API_KEY")) as client:
        response = client.chat.send(
            model="openrouter/free",
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        print(response.choices[0].message.content)