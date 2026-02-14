# 🧠 Meeting Action Items Tracker

An AI-powered mini workspace that extracts structured action items from meeting transcripts and allows users to manage them efficiently.

Built as part of an AI-Native Full Stack assignment.

---

## 🚀 Live Features

### ✅ Core Functionality
- Paste meeting transcript
- Extract action items using Groq LLM
- Auto-detect:
  - Task
  - Owner (if mentioned)
  - Due date (if mentioned)
- Edit action items
- Add new action items manually
- Delete action items
- Mark items as Done
- Filter (All / Open / Completed)

### 📊 Dashboard Metrics
- Total transcripts
- Total action items
- Completed items
- Completion %

### 📜 History
- View last 5 processed transcripts
- Open previous transcript items
- Delete transcripts

### ⚙️ Status Page
- Backend health indicator
- Database status
- Groq LLM connection status
- LLM test button

---

## 🏗 Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python
- **Database:** SQLite
- **LLM Provider:** Groq
- **Model:** Llama 3
- **Environment Config:** dotenv

---

## 🛠 Installation (Local Run)

### 1️⃣ Clone the repository

```bash
git clone <your-repo-link>
cd meeting-action-tracker
2️⃣ Install dependencies
pip install -r requirements.txt
3️⃣ Create .env file
GROQ_API_KEY=your_groq_api_key_here
4️⃣ Run the app
streamlit run app.py
🌍 Deployment
Designed to be deployed on:

Streamlit Cloud

Render

Railway

Docker-based environments

The app is built without hardcoded API keys and supports environment-based configuration.

📁 Project Structure
meeting-action-tracker/
│
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── AI_NOTES.md
├── PROMPTS_USED.md
├── ABOUTME.md
│
├── utils/
│   ├── extractor.py
│   └── storage.py
│
└── data/
🔐 Security Notes
No API keys stored in code

Uses .env for secrets

.env excluded via .gitignore

📌 Assignment Requirements Covered
✔ Transcript input
✔ AI extraction
✔ CRUD operations
✔ Done status
✔ History (last 5)
✔ Status page
✔ Error handling
✔ Hosting-ready structure

👩‍💻 Author
Usha Rani
AI-focused Full Stack Developer