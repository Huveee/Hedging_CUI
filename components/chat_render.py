import streamlit as st
import html

def render_chat(messages, loading=False):
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

    /* Typing Helper Animation */
    .typing-indicator {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 24px;
    }
    .typing-indicator span {
      display: block;
      width: 6px;
      height: 6px;
      background-color: #555;
      border-radius: 50%;
      margin: 0 2px;
      animation: typing 1.4s infinite ease-in-out both;
    }
    .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
    .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
      0%, 80%, 100% { transform: scale(0); }
      40% { transform: scale(1); }
    }
    </style>
    """, unsafe_allow_html=True)

    rows = []
    for msg in messages:
        role = msg["role"]
        side = "right" if role == "user" else "left"
        cls = "user" if role == "user" else "assistant"
        # Escape just in case
        safe = html.escape(msg["content"])
        rows.append(f'<div class="msg-row {side}"><div class="bubble {cls}">{safe}</div></div>')

    if loading:
        # Add a assistant bubble with typing indicator
        rows.append(
            '<div class="msg-row left">'
            '<div class="bubble assistant">'
            '<div class="typing-indicator">'
            '<span></span><span></span><span></span>'
            '</div>'
            '</div>'
            '</div>'
        )

    chat_html = '<div class="chat-wrap">' + "".join(rows) + "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)