# src/llm/token_counter.py

def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in text
    
    Fallback: 1 token ≈ 4 characters (rough estimation)
    
    Args:
        text: The text to count tokens for
        
    Returns:
        Estimated token count
    """
    # Rough estimation: 1 token ≈ 4 characters
    return max(1, len(text) // 4)

