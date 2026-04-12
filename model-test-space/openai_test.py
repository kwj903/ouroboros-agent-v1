from openai import OpenAI
import os

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

response = client.responses.create(
    model="gpt-5.4-mini",
    input="한국어로 짧게 인사해줘."
)

print(response.output_text)