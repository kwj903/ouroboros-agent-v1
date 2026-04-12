from google import genai

client = genai.Client()

while True:
    prompt = input("질문을 입력하세요: ")
    response = client.models.generate_content(
        model="gemma-4-31b-it",
        contents=prompt
    )
    print(response.text)
    print(response.usage_metadata)
