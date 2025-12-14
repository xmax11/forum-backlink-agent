from llm_client import call_llm


def generate_anchors(domain_text, brand, model="llama-3.3-70b-versatile"):
    """
    Generates a list of natural, SEO-friendly anchor texts
    based on your domain content and brand.

    Parameters:
        domain_text (str): Extracted text/content from your website.
        brand (str): Brand name to include in anchor variations.
        model (str): Groq model name.

    Returns:
        list[str]: A list of anchor texts.
    """

    prompt = f"""
You are an SEO expert. Generate 10 natural, diverse, human-like anchor texts
that could be used to link back to the website content below.

Rules:
- Anchors must be short (2–6 words)
- Must sound natural in forum replies
- Include the brand "{brand}" in 2–3 anchors
- Avoid keyword stuffing
- Avoid exact-match repetition
- Make them varied and human

Website content:
\"\"\"
{domain_text}
\"\"\"
"""

    messages = [
        {"role": "system", "content": "You generate natural SEO anchor texts."},
        {"role": "user", "content": prompt}
    ]

    response = call_llm(messages, model=model)
    anchors = [a.strip("-• ").strip() for a in response.split("\n") if a.strip()]

    return anchors
