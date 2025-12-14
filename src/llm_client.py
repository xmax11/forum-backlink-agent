import os
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def call_llm(messages, model="llama-3.3-70b-versatile", temperature=0.7):
    """
    Sends a chat completion request to Groq's API.

    Parameters:
        messages (list): [{"role": "system"|"user"|"assistant", "content": "..."}]
        model (str): Groq model name
        temperature (float): creativity level

    Returns:
        str: The assistant's message content
    """

    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY environment variable is not set.")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    response = requests.post(
        GROQ_API_URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    if not response.ok:
        raise RuntimeError(
            f"Groq API error {response.status_code}: {response.text}"
        )

    data = response.json()
    return data["choices"][0]["message"]["content"]
