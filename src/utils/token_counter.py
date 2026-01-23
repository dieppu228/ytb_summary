def estimate_tokens(text):
    """
    Estimate the number of tokens in text
    Rough estimation: 1 token ≈ 4 characters
    """
    if text is None:
        return 0

    if not isinstance(text, str):
        text = str(text)

    text = text.strip()
    if not text:
        return 0

    return max(1, len(text) // 4)