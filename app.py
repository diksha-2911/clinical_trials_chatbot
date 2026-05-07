import streamlit as st
from src.data_loader import load_all_documents
from src.vectorstore import FaissVectorStore
from src.search import RAGChatbot
from src.clinical_trials_loader import load_clinical_trials
from PIL import Image
import base64

icon = Image.open("assets/icon.jpeg")

def get_base64_image(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode()

logo = get_base64_image("assets/icon.jpeg")
st.set_page_config(
    page_title="Clinical Trials Chatbot",
    page_icon=icon,
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');
 
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
 
html, body, [data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stHeader"] {
    background: #0d0f14 !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
}
 
#MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], header { display: none !important; }
 
[data-testid="stMain"] > div { padding: 0 !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }
 
/* ── Top bar ── */
.rag-topbar {
    position: sticky; top: 0; z-index: 100;
    background: #0d0f14;
    border-bottom: 1px solid #1e2330;
    padding: 18px 40px;
    display: flex; align-items: center; gap: 14px;
}
# .rag-topbar-icon {
#     width: 36px; height: 36px;
#     background: linear-gradient(135deg, #4f8ef7, #a66cf7);
#     border-radius: 10px;
#     display: flex; align-items: center; justify-content: center;
#     font-size: 18px;
}
.rag-topbar-icon img {
    width: 36px; height: 36px;
    border-radius: 10px;
    object-fit: contain;
}         
.rag-topbar-title {
    font-family: 'Syne', sans-serif;
    font-size: 20px; font-weight: 700;
    color: #f0ece4; letter-spacing: -0.3px;
}
.rag-topbar-sub {
    font-size: 12px; color: #6b7280;
    margin-left: auto; font-weight: 300;
}
 
/* ── Chat area ── */
.chat-wrapper {
    max-width: 820px; margin: 0 auto;
    padding: 32px 24px 160px;
    display: flex; flex-direction: column; gap: 24px;
}
 
/* ── Message bubbles ── */
.msg-row {
    display: flex; gap: 14px; align-items: flex-start;
    animation: fadeUp 0.3s ease both;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.msg-row.user { flex-direction: row-reverse; }
            
 
.msg-avatar {
    width: 34px; height: 34px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; flex-shrink: 0;
}
.avatar-user { background: #1e2330; }
.avatar-bot  { background: linear-gradient(135deg, #4f8ef7 0%, #a66cf7 100%); }
 
.msg-bubble {
    max-width: 78%; padding: 14px 18px;
    border-radius: 16px; line-height: 1.65;
    font-size: 14.5px; font-weight: 300;
}
            

                      
.bubble-user {
    background: #1a1f2e; border: 1px solid #2a3148;
    border-top-right-radius: 4px; color: #d4cfc7;
}
.bubble-bot {
    background: #111520; border: 1px solid #1e2330;
    border-top-left-radius: 4px; color: #e2ddd5;
}
.bubble-bot strong { color: #7eb3fa; font-weight: 500; }
.bubble-bot code {
    background: #1a1f2e; padding: 2px 6px;
    border-radius: 4px; font-size: 13px; color: #a78bfa;
}
 
/* ── Source chips ── */
.sources-row {
    display: flex; flex-wrap: wrap; gap: 6px;
    margin-top: 10px; padding-top: 10px;
    border-top: 1px solid #1e2330;
}
.source-chip {
    background: #1a1f2e; border: 1px solid #2a3148;
    border-radius: 20px; padding: 3px 10px;
    font-size: 11.5px; color: #7eb3fa; font-weight: 400;
}
 
/* ── Empty / welcome state ── */
.empty-state {
    text-align: center;
    padding: 80px 24px 40px;
    animation: fadeUp 0.5s ease both;
}
.empty-state-logo { font-size: 48px; margin-bottom: 20px; }
.empty-state h2 {
    font-family: 'Syne', sans-serif;
    font-size: 26px; font-weight: 700;
    color: #f0ece4; margin-bottom: 10px; letter-spacing: -0.5px;
}
.empty-state p {
    color: #6b7280; font-size: 14px;
    max-width: 420px; margin: 0 auto 32px; line-height: 1.7;
}
 
/* Starter buttons */
div[data-testid="stButton"] > button {
    background: #111520 !important;
    border: 1px solid #1e2330 !important;
    border-radius: 12px !important;
    color: #9ca3af !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 300 !important;
    text-align: left !important;
    padding: 14px 16px !important;
    transition: border-color 0.2s, color 0.2s !important;
    height: auto !important;
    white-space: normal !important;
}
div[data-testid="stButton"] > button:hover {
    border-color: #4f8ef7 !important;
    color: #e8e4dc !important;
    background: #111520 !important;
}
 
/* ── Chat input overrides ── */
[data-testid="stChatInput"] > div {
    background: #111520 !important;
    border: 1px solid #2a3148 !important;
    border-radius: 16px !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #4f8ef7 !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14.5px !important;
    font-weight: 300 !important;
    caret-color: #4f8ef7 !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #4b5563 !important; }
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #4f8ef7, #a66cf7) !important;
    border-radius: 10px !important; border: none !important;
}
 
[data-testid="stSpinner"] > div { border-top-color: #4f8ef7 !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource(show_spinner=False)
def init_rag():
    
    store = FaissVectorStore("faiss_store")
    store.load()
    chatbot = RAGChatbot()
    return store, chatbot

if "messages" not in st.session_state:
    # Each entry: {role: "user"|"assistant", content: str, sources: list[str]}
    st.session_state.messages = []

# def get_base64_image(image_path):
#     with open(image_path, "rb") as f:
#         return base64.b64encode(f.read()).decode()

# img_base64 = get_base64_image("icon.jpeg")

st.markdown(f"""
<div class="rag-topbar">
    <div class="rag-topbar-icon"> <img src="data:image/png;base64,{logo}" width="24"></div>
    <div class="rag-topbar-title">ClinIntel</div>
    <div class="rag-topbar-sub">Made for Demo</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
 
if not st.session_state.messages:
    # Welcome / empty state
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-logo">🧠</div>
        <h2>Ask Questions Across Your Clinical Documents</h2>
        <p>I search through clinical trial databases, study protocols, and medical knowledge sources to return concise, evidence-based answers.</p>
    </div>
    """, unsafe_allow_html=True)
 
    # starters = [
    #     ("💡", "What is attention mechanism?"),
    #     ("📐", "Explain transformer architecture"),
    #     ("⚡", "How does FAISS indexing work?"),
    #     ("🔗", "What is RAG and how does it work?"),
    # ]
    # cols = st.columns(2)
    # for i, (icon, label) in enumerate(starters):
    #     with cols[i % 2]:
    #         if st.button(f"{icon}  {label}", key=f"starter_{i}", use_container_width=True):
    #             st.session_state["prefill_query"] = label
    #             st.rerun()
 
else:
    for msg in st.session_state.messages:
        role    = msg["role"]
        content = msg["content"]
        sources = msg.get("sources", [])
 
        if role == "user":
            st.markdown(f"""
            <div class="msg-row user">
                <div class="msg-avatar avatar-user">👤</div>
                <div class="msg-bubble bubble-user">{content}</div>
            </div>""", unsafe_allow_html=True)
        else:
            sources_html = ""
            if sources:
                chips = "".join(
                    f'<span class="source-chip">📄 {s}</span>' for s in sources
                )
                sources_html = f'<div class="sources-row">{chips}</div>'
 
            st.markdown(f"""
            <div class="msg-row">
                <div class="msg-avatar avatar-bot">✦</div>
                <div class="msg-bubble bubble-bot">
                    {content}{sources_html}
                </div>
            </div>""", unsafe_allow_html=True)
 
st.markdown('</div>', unsafe_allow_html=True)

prefill    = st.session_state.pop("prefill_query", "")
user_input = st.chat_input(" Ask a question about your documents…")
 
# Starter-button injection
if prefill and not user_input:
    user_input = prefill

if user_input and user_input.strip():
    query = user_input.strip()
 
    st.session_state.messages.append({"role": "user", "content": query})
 
    with st.spinner("Thinking…"):
        try:
            _, chatbot = init_rag()
 
            # Pass full conversation history so search_and_summarize can use it
            # (you'll wire this up when you share that function)
            result = chatbot.chat(
                query,
                top_k=3,
                chat_history=st.session_state.messages[:-1],  # exclude current user msg
            )
 
            # Handles both a plain string response and a dict response
            if isinstance(result, dict):
                answer  = result.get("summary") or result.get("answer") or str(result)
                sources = result.get("sources", [])
            else:
                answer  = str(result)
                sources = []
 
        except TypeError:
            # If current search_and_summarize doesn't accept chat_history yet,
            # fall back gracefully — no changes needed to your existing function.
            try:
                result  = chatbot.chat(query, top_k=3)
                answer  = result.get("summary", str(result)) if isinstance(result, dict) else str(result)
                sources = result.get("sources", []) if isinstance(result, dict) else []
            except Exception as e:
                answer, sources = f"⚠️ Error: {e}", []
 
        except Exception as e:
            answer, sources = f"⚠️ Error: {e}", []
 
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })
 
    st.rerun()

# Example usage
# if __name__ == "__main__":
    
#     # docs = load_all_documents("data")
#     docs = load_clinical_trials("data/trials.json")

#     store = FaissVectorStore("faiss_store")
#     store.build_from_documents(docs)
    # store.load()
    # #print(store.query("What is attention mechanism?", top_k=3))
    # # rag_search = RAGSearch()
    # # query = "What is attention mechanism?"
    # # summary = rag_search.search_and_summarize(query, top_k=3)
    # # print("Summary:", summary)

    # chatbot = RAGChatbot()

    # response = chatbot.chat("What is attention mechanism?")
    # print(response)

    # response = chatbot.chat("Can you explain that in simpler words?")
    # print(response)