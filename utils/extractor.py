import os
import json
import re
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def extract_action_items(transcript):
    """Extract structured action items using Groq with smart fallback"""

    if not GROQ_API_KEY:
        return smart_fallback(transcript)

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are an AI assistant that extracts structured action items.

Rules:
- Extract only actionable tasks.
- If transcript format is "Name: sentence", use Name as owner.
- If no due date mentioned, return empty string.
- Return STRICT JSON only.
- No explanation. No markdown.

Format:
[
  {{
    "task": "short actionable task",
    "owner": "person responsible",
    "due_date": "YYYY-MM-DD or empty"
  }}
]

Transcript:
{transcript}
"""

    data = {
        "model": "llama-3.1-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 800
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()["choices"][0]["message"]["content"]

        # Extract JSON safely
        json_match = re.search(r"\[.*\]", result, re.DOTALL)
        if json_match:
            items = json.loads(json_match.group())

            cleaned = []
            for item in items:
                task = item.get("task", "").strip()
                owner = item.get("owner", "").strip()
                due_date = item.get("due_date", "").strip()

                # Basic date normalization attempt
                if due_date:
                    try:
                        parsed = datetime.strptime(due_date, "%Y-%m-%d")
                        due_date = parsed.strftime("%Y-%m-%d")
                    except:
                        pass

                if task:
                    cleaned.append({
                        "task": task,
                        "owner": owner,
                        "due_date": due_date
                    })

            if cleaned:
                return cleaned

    except Exception:
        pass

    # Fallback if LLM fails
    return smart_fallback(transcript)


# -----------------------------
# SMART FALLBACK
# -----------------------------

def smart_fallback(transcript):
    """
    Extract basic action items using rule-based logic.
    Detects 'Name: sentence' format.
    """

    items = []

    for line in transcript.split("\n"):
        line = line.strip()
        if not line:
            continue

        # Detect Name: pattern
        match = re.match(r"^(.*?):\s*(.*)", line)
        if match:
            owner = match.group(1).strip()
            sentence = match.group(2).strip()

            # Only capture actionable lines
            if any(word in sentence.lower() for word in ["will", "prepare", "review", "send", "complete", "submit"]):
                items.append({
                    "task": sentence,
                    "owner": owner,
                    "due_date": ""
                })

    return items[:5]
