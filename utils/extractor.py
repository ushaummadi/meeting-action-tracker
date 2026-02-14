import os
import json
import re
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def extract_action_items(transcript: str):
    """
    Extract structured action items using Groq.
    Falls back to rule-based extraction if LLM fails.
    Always returns a list of dicts:
    [
        {"task": "...", "owner": "...", "due_date": "..."}
    ]
    """

    if not transcript.strip():
        return []

    # If no API key → fallback immediately
    if not GROQ_API_KEY:
        return smart_fallback(transcript)

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are an AI system that extracts structured action items.

STRICT RULES:
1. Every task sentence becomes one action item.
2. If format is "Name: sentence":
   - owner = Name
   - task = sentence (without name)
3. Extract ALL tasks.
4. If no due date mentioned → due_date = "".
5. Return ONLY a valid JSON list.
6. No explanations. No markdown. No extra text.

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

        # Safely extract JSON list
        json_match = re.search(r'\[[\s\S]*?\]', result)
        if json_match:
            parsed_items = json.loads(json_match.group())

            cleaned = []

            for item in parsed_items:
                task = item.get("task", "").strip()
                owner = item.get("owner", "").strip()
                due_date = item.get("due_date", "").strip()

                # Normalize date format if valid
                if due_date:
                    try:
                        parsed_date = datetime.strptime(due_date, "%Y-%m-%d")
                        due_date = parsed_date.strftime("%Y-%m-%d")
                    except:
                        due_date = ""

                if task:
                    cleaned.append({
                        "task": task,
                        "owner": owner,
                        "due_date": due_date
                    })

            if cleaned:
                return cleaned

    except Exception as e:
        print("LLM extraction failed:", e)

    # If anything fails → fallback
    return smart_fallback(transcript)


# ---------------------------------------------------
# SMART FALLBACK (RULE-BASED EXTRACTION)
# ---------------------------------------------------

def smart_fallback(transcript: str):
    """
    Basic rule-based extraction:
    Detects 'Name: sentence'
    """

    items = []

    for line in transcript.split("\n"):
        line = line.strip()
        if not line:
            continue

        # Detect Name: sentence
        match = re.match(r"^(.*?):\s*(.*)", line)
        if match:
            owner = match.group(1).strip()
            sentence = match.group(2).strip()

            # Basic action detection
            if any(word in sentence.lower() for word in [
                "will", "prepare", "review", "send",
                "complete", "submit", "finalize"
            ]):
                items.append({
                    "task": sentence,
                    "owner": owner,
                    "due_date": ""
                })

    return items[:10]
