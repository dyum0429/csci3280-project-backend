from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_response(transcript: str, chat_history: list = []) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful assistant responding to voice messages. Keep responses concise and conversational."},
        *chat_history,
        {"role": "user", "content": transcript}
    ]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=150
    )
    return response.choices[0].message.content