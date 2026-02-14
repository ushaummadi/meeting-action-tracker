import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def extract_action_items(transcript):
    """Direct Groq API call - bulletproof"""
    if not GROQ_API_KEY:
        return []
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Extract action items from this transcript as JSON ONLY.

Return ONLY: [{{"task": "description", "owner": "name", "due_date": "YYYY-MM-DD"}}]

Transcript:
{transcript}"""
    
    data = {
        "model": "llama-3.1-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(GROQ_URL, headers=headers, json=data, timeout=30)
        result = response.json()['choices'][0]['message']['content']
        
        # Extract JSON from response
        json_match = re.search(r'\[.*\]', result, re.DOTALL)
        if json_match:
            items = json.loads(json_match.group())
            if isinstance(items, list):
                return [{
                    'task': item.get('task', '').strip(),
                    'owner': item.get('owner', '').strip(),
                    'due_date': item.get('due_date', '').strip()
                } for item in items if item.get('task')]
    except:
        pass
    
    # Fallback patterns
    fallback = []
    for line in transcript.split('\n'):
        if any(word in line.lower() for word in ['will ', 'to ', 'prepare', 'review', 'send']):
            fallback.append({'task': line.strip()[:100], 'owner': '', 'due_date': ''})
    return fallback[:5]
