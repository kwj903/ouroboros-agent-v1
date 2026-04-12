import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

while True:
    prompt = input("질문을 입력하세요: ")
    chat_completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    print(chat_completion.choices[0].message.content)
