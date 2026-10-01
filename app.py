import streamlit as st

import prompts
import ui
from gemini_client import ask, summarize
from senders import TOOLS

st.set_page_config(page_title="Snap & Study", page_icon="📸")
ui.inject_css()

if not prompts.SYSTEM_PROMPT.strip() or not prompts.SUMMARY_PROMPT.strip():
    st.error("Fill in SYSTEM_PROMPT and SUMMARY_PROMPT in prompts.py first.")
    st.stop()


def secret(key, default=None):
    """st.secrets raises if no secrets file exists yet, so wrap it."""
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


if not secret("GEMINI_API_KEY"):
    ui.wordmark_small()
    st.warning(
        "No Gemini key yet. Copy `.streamlit/secrets.toml.example` to "
        "`.streamlit/secrets.toml` and add your keys, then refresh."
    )
    st.stop()

tool_name = secret("ACTION_TOOL", "email")
tool = TOOLS[tool_name]

QUICK_STARTS = ["Explain this", "Show me the steps", "What's the key idea?"]

if "destination" not in st.session_state:
    st.session_state.destination = ""
    st.session_state.history = []
    st.session_state.sent_image_id = None
    st.session_state.uploader_key = 0


def new_chat():
    st.session_state.history = []
    st.session_state.sent_image_id = None
    st.session_state.uploader_key += 1  # new key = empty uploader


# ---------- onboarding ----------
def onboarding():
    ui.hero(tool["where"])
    with st.form("onboarding"):
        dest = st.text_input(tool["label"], placeholder=tool["placeholder"])
        st.caption(tool["hint"])
        go = st.form_submit_button("Start studying", type="primary")
    if go:
        dest = dest.strip()
        if tool_name == "whatsapp":
            dest = dest.replace(" ", "").replace("-", "")
        if tool["valid"](dest):
            st.session_state.destination = dest
            st.rerun()
        else:
            st.warning(f"That doesn't look like a valid {tool['label'].lower().replace('your ', '')}. Check it and try again.")


# ---------- chat ----------
def top_bar():
    name, dest, change = st.columns([2, 3, 1.1], vertical_alignment="center")
    with name:
        ui.wordmark_small()
    with dest:
        ui.sending_to(st.session_state.destination)
    with change:
        if st.button("Change", key="change_dest"):
            st.session_state.destination = ""
            new_chat()
            st.rerun()


def render_history():
    for m in st.session_state.history:
        role = "user" if m["role"] == "user" else "assistant"
        with st.chat_message(role):
            if m.get("image"):
                st.image(m["image"], width=240)
            st.markdown(m["text"])


def chat():
    top_bar()

    pick, preview = st.columns([3, 2], vertical_alignment="center")
    with pick:
        image = st.file_uploader(
            "Add a photo of your problem, diagram or notes",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"upload_{st.session_state.uploader_key}",
        )
    with preview:
        if image:
            ui.photo_preview(image.getvalue(), image.type, image.name)

    history = st.session_state.history
    quick = None
    if not history:
        if image:
            cols = st.columns(len(QUICK_STARTS))
            for col, label in zip(cols, QUICK_STARTS):
                if col.button(label, key=f"quick_{label}"):
                    quick = label
        else:
            ui.hint("Start with a photo of what you're stuck on. You can also just type a question.")

    render_history()

    prompt = st.chat_input("Ask about it, or type 'explain this'") or quick
    if prompt:
        msg = {"role": "user", "text": prompt}
        # attach each uploaded image only once
        if image and image.file_id != st.session_state.sent_image_id:
            msg["image"] = image.getvalue()
            msg["mime"] = image.type
            st.session_state.sent_image_id = image.file_id
        history.append(msg)

        with st.spinner("Reading your photo..." if "image" in msg else "Thinking..."):
            try:
                reply = ask(history)
            except Exception as e:
                history.pop()
                if "RESOURCE_EXHAUSTED" in str(e):
                    st.error("Today's free Gemini quota is used up for every model in MODELS. It resets at midnight Pacific time (about 12:30 PM in India).")
                elif getattr(e, "code", None) == 503 or "503 UNAVAILABLE" in str(e):
                    st.error("Gemini is temporarily busy. Please wait a minute and try again.")
                else:
                    st.error(f"Gemini didn't answer. Try again in a moment. If it keeps failing, check GEMINI_API_KEY. ({e})")
                st.stop()
        history.append({"role": "model", "text": reply})
        st.rerun()

    if history:
        send_col, new_col, _ = st.columns([2, 1.3, 2])
        if send_col.button(tool["button"], type="primary", key="send"):
            with st.spinner("Sending..."):
                try:
                    receipt = tool["send"](st.session_state.destination, summarize(history))
                    if tool_name == "whatsapp":
                        st.success("Your study note was sent to WhatsApp.")
                        st.caption(f"Sent to WhatsApp · {receipt['sid']}")
                    else:
                        st.toast(f"Sent to {st.session_state.destination}", icon="✅")
                except Exception as e:
                    st.error(f"Couldn't send. Check your {tool['where']} settings in secrets.toml. ({e})")
        if new_col.button("New chat", key="new_chat"):
            new_chat()
            st.rerun()


if st.session_state.destination:
    chat()
else:
    onboarding()