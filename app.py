import streamlit as st
import os
from dotenv import load_dotenv
from datetime import date

from utils.extractor import extract_action_items
from utils.storage import (
    init_db,
    add_transcript,
    get_recent_transcripts,
    get_action_items,
    save_action_items,
    update_action_item,
    delete_action_item,
    delete_transcript
)

# ========================================
# CONFIG
# ========================================

st.set_page_config(
    page_title="Meeting Action Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()
init_db()

# ========================================
# SESSION STATE INIT
# ========================================

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "current_ts_id" not in st.session_state:
    st.session_state.current_ts_id = None

page = st.session_state.page

# ========================================
# HEADER
# ========================================

header_left, header_right = st.columns([5, 1])

with header_left:
    st.markdown("<h2>Turn messy transcripts into crisp action items</h2>", unsafe_allow_html=True)
    st.caption("AI-powered extraction using Groq")

with header_right:
    c1, c2 = st.columns(2)
    if c1.button("History"):
        st.session_state.page = "History"
        st.rerun()
    if c2.button("Status"):
        st.session_state.page = "Status"
        st.rerun()

st.divider()

# ========================================
# SIDEBAR
# ========================================

with st.sidebar:

    st.markdown("### Navigation")

    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "Home"
        st.rerun()

    if st.button("📝 Process", use_container_width=True):
        st.session_state.page = "Process"
        st.rerun()

    if st.button("📋 Items", use_container_width=True):
        st.session_state.page = "Items"
        st.rerun()

    if st.button("📜 History", use_container_width=True):
        st.session_state.page = "History"
        st.rerun()

    if st.button("🔧 Status", use_container_width=True):
        st.session_state.page = "Status"
        st.rerun()

    st.divider()

    if st.button("🗑️ Clear Data", use_container_width=True):
        init_db()
        st.session_state.current_ts_id = None
        st.success("Database reset.")
        st.rerun()

# ========================================
# HOME PAGE
# ========================================

if page == "Home":

    transcripts = get_recent_transcripts()
    transcripts_count = len(transcripts)

    total_items = 0
    completed_items = 0

    for t in transcripts:
        items = get_action_items(t["id"])
        total_items += len(items)
        completed_items += sum(1 for i in items if i["done"])

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Transcripts", transcripts_count)
    col2.metric("Action Items", total_items)
    col3.metric("Completed", completed_items)

    completion_rate = int((completed_items / total_items) * 100) if total_items > 0 else 0
    col4.metric("Completion %", f"{completion_rate}%")

# ========================================
# PROCESS PAGE
# ========================================

elif page == "Process":

    st.subheader("Paste transcript and extract action items")

    transcript = st.text_area("Transcript", height=250)

    if st.button("Extract", type="primary"):

        if not transcript.strip():
            st.warning("Transcript cannot be empty.")
        else:
            try:
                with st.spinner("Extracting..."):
                    items = extract_action_items(transcript)

                if items:
                    ts_id = add_transcript(transcript, items)
                    save_action_items(ts_id, items)
                    st.session_state.current_ts_id = ts_id
                    st.session_state.page = "Items"
                    st.success(f"{len(items)} action items extracted.")
                    st.rerun()
                else:
                    st.error("No action items found.")

            except Exception as e:
                st.error("LLM extraction failed. Check API key or connection.")
                st.exception(e)

# ========================================
# ITEMS PAGE
# ========================================

elif page == "Items":

    if not st.session_state.current_ts_id:
        
        st.info("Process a transcript first.")
    else:
        ts_id = st.session_state.current_ts_id
        items = sorted(get_action_items(ts_id), key=lambda x: x["done"])

        if st.button("➕ Add New Action Item"):
            items.append({
                "task": "New Task",
                "owner": "",
                "due_date": "",
                "done": False
            })
            save_action_items(ts_id, items)
            st.rerun()

        if not items:
            st.info("No action items found.")
        else:

            filter_option = st.selectbox("Filter", ["All", "Open", "Completed"])

            for item in items:

                if filter_option == "Open" and item["done"]:
                    continue
                if filter_option == "Completed" and not item["done"]:
                    continue

                with st.container(border=True):

                    col1, col2, col3, col4 = st.columns([4,2,2,1])

                    task = col1.text_input("Task", value=item["task"], key=f"task_{item['id']}")
                    owner = col2.text_input("Owner", value=item["owner"], key=f"owner_{item['id']}")

                    saved_date = item["due_date"]
                    if saved_date:
                        try:
                            saved_date = date.fromisoformat(saved_date)
                        except:
                            saved_date = date.today()
                    else:
                        saved_date = date.today()

                    due_date = col3.date_input(
                        "Due Date",
                        value=saved_date,
                        key=f"due_{item['id']}"
                    )
                    done = col4.checkbox("Done", value=bool(item["done"]), key=f"done_{item['id']}")

                    if done != bool(item["done"]):
                        update_action_item(item["id"], ts_id, task, owner, str(due_date), done)
                        st.rerun()

                    b1, b2 = st.columns(2)

                    if b1.button("Save", key=f"save_{item['id']}"):
                        if not task.strip():
                            st.warning("Task cannot be empty.")
                        else:
                            update_action_item(item["id"], ts_id, task, owner, str(due_date), done)
                            st.success("Updated")
                            st.rerun()

                    if b2.button("Delete", key=f"del_item_{item['id']}"):
                        delete_action_item(item["id"], ts_id)
                        st.success("Deleted")
                        st.rerun()

# ========================================
# HISTORY PAGE
# ========================================

elif page == "History":

    transcripts = get_recent_transcripts(5)

    if not transcripts:
        st.markdown("### 👋 No transcripts yet")
        st.write("Go to **Process** and extract your first transcript.")
    else:
        for t in transcripts:

            with st.container(border=True):

                left, right = st.columns([6,2])

                left.markdown(f"**{t['transcript'][:60]}...**")
                left.caption(f"{t['created_at']} | {len(t.get('action_items', []))} items")

                c1, c2 = right.columns(2)

                if c1.button("Open", key=f"open_{t['id']}", use_container_width=True):
                    st.session_state.current_ts_id = t["id"]
                    st.session_state.page = "Items"
                    st.rerun()

                if c2.button("Delete", key=f"delete_{t['id']}", use_container_width=True):
                    st.caption("⚠ This action cannot be undone")
                    delete_transcript(t["id"])
                    st.success("Transcript deleted.")
                    st.rerun()

# ========================================
# STATUS PAGE
# ========================================

elif page == "Status":

    col1, col2, col3 = st.columns(3)

    col1.metric("Backend", "Healthy")
    col2.metric("Database", f"{len(get_recent_transcripts())} transcripts")

    groq_status = "Connected" if os.getenv("GROQ_API_KEY") else "Missing Key"
    col3.metric("Groq AI", groq_status)

    st.divider()

    if st.button("Test LLM Connection"):
        try:
            extract_action_items("Test task: John will submit report tomorrow.")
            st.success("LLM working correctly.")
        except:
            st.error("LLM test failed.")
