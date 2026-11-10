def classify_reply_intent(body: str) -> str:
    """
    Mock LLM intent classifier.
    Replace this body with a local Ollama / LLM call returning JSON:
    e.g., ollama.chat(model='llama3.2', messages=[...])
    """
    text = body.lower()
    if any(word in text for word in ["unsubscribe", "remove me", "stop", "opt out"]):
        return "OPT_OUT"
    if any(word in text for word in ["not interested", "no thanks", "pass"]):
        return "DECLINED"
    if any(word in text for word in ["interested", "call", "chat", "tell me more", "yes"]):
        return "RESPONDED"
    return "RESPONDED"
