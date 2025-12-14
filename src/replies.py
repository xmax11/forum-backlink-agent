from llm_client import call_llm


def generate_reply(thread_title, thread_text, anchor, domain, model="llama-3.3-70b-versatile"):
    """
    Generates a natural, human-like forum reply that includes the given anchor.

    Parameters:
        thread_title (str): Title of the forum thread.
        thread_text (str): Extracted text from the thread.
        anchor (str): Anchor text to include in the reply.
        domain (str): Your website domain.
        model (str): Groq model name.

    Returns:
        str: A forum-ready reply.
    """

    prompt = f"""
Write a natural, helpful forum reply to the thread below.
The reply must sound human, conversational, and relevant.

Rules:
- Include this anchor exactly once: "{anchor}"
- The anchor must link to: {domain}
- Do NOT sound promotional
- Do NOT force keywords
- Keep it short (2–4 sentences)
- Make it fit naturally into the discussion

Thread Title:
{thread_title}

Thread Content:
\"\"\"
{thread_text}
\"\"\"
"""

    messages = [
        {"role": "system", "content": "You write natural, human-like forum replies."},
        {"role": "user", "content": prompt}
    ]

    reply = call_llm(messages, model=model)

    # Ensure anchor is present
    if anchor not in reply:
        reply += f" ({anchor})"

    return reply.strip()
