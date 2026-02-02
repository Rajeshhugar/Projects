from groq import Groq

from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)


def read_text_file(file_path):
    """Reads a text file and returns its content as a string."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"File not found: {file_path}")

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are someone who is professional in getting data from HTML strings. Users will be passing HTML string of news websites you will have to get Title, Date and Content from this string."
        },
        {
            "role": "user",
            "content": read_text_file("news_output.txt"),
        }
    ],
    model="llama-guard-3-8b",
    temperature=0.5,
    max_completion_tokens=1024,
    top_p=1,
    stop=None,
    stream=False,
)

print(chat_completion.choices[0].message.content)