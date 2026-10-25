import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1"

def summarize_with_ollama(facility, facts):
    prompt = f"""You are writing a short summary for a college administrator.

Facility: {facility}

Facts taken from student feedback:
{facts}

Write 3 to 4 simple sentences. Start with the overall rating, then the
biggest concerns, then the better areas. Always say "mentions", never
"comments". Only talk about the areas listed in the facts. Never mention
any other area. Use the words "few complaints" only for areas in the list
called "Areas with few complaints". For areas in the "still often
criticised" list, say they are less negative than other areas but still
criticised, and never say "few complaints" for them. Do not add a closing
or wrap-up sentence. Never say "students like" or "students appreciate".
Do not start with "Students generally". Refer to the facility as "the
{facility}", not "our". Use only the facts above. Do not invent numbers,
causes or problems. Do not copy the facts word for word."""

    reply = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3},
        },
        timeout=180,
    )
    reply.raise_for_status()
    return reply.json()["response"].strip()