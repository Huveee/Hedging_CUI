import streamlit as st
import html

def render_chat(messages):
    st.markdown("""
    <style>
    .chat-wrap {
      height: 50vh;
      min-height: 300px;
      max-height: 700px;
      overflow-y: auto;
      padding: 12px;
      border: 1px solid rgba(255,255,255,0.15);
      border-radius: 10px;
      background: transparent;
    }

    .msg-row { display: flex; margin: 8px 0; }
    .msg-row.left { justify-content: flex-start; }
    .msg-row.right { justify-content: flex-end; }

    .bubble {
      max-width: 75%;
      padding: 10px 12px;
      border-radius: 14px;
      line-height: 1.35;
      border: 1px solid rgba(255,255,255,0.15);
      background: #ffffff;
      white-space: pre-wrap;
      word-wrap: break-word;
      color: #111 !important;
      opacity: 1 !important;
      box-sizing: border-box;
    }

    .bubble.user { background: #e9f2ff; }
    .bubble.assistant { background: #ffffff; }
    .bubble * { color: #111 !important; opacity: 1 !important; }
    </style>
    """, unsafe_allow_html=True)

    rows = []
    for msg in messages:
        role = msg["role"]
        side = "right" if role == "user" else "left"
        cls = "user" if role == "user" else "assistant"
        safe = html.escape(msg["content"])
        rows.append(f'<div class="msg-row {side}"><div class="bubble {cls}">{safe}</div></div>')

    chat_html = '<div class="chat-wrap">' + "".join(rows) + "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)