"""Look and feel for Snap & Study: a notebook page with a taped-in photo.

Everything visual lives here so app.py stays about behaviour.
"""
import base64
import html

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,800&family=Newsreader:opsz,wght@6..72,400;6..72,600;6..72,700&display=swap');

:root {
  --paper: #F3F6FB;
  --grid: #DCE4F2;
  --ink: #1B2A5B;
  --ink-soft: #4B5B8E;
  --marker: #FFE45C;
  --margin: #E4572E;
  --pad: clamp(88px, calc(50vw - 22rem), 30vw);
  --sans: 'Bricolage Grotesque', system-ui, sans-serif;
  --serif: 'Newsreader', Georgia, serif;
}

/* ---- page: graph paper with a margin line ---- */
.stApp {
  background-color: var(--paper);
  background-image:
    linear-gradient(var(--grid) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid) 1px, transparent 1px);
  background-size: 28px 28px;
  color: var(--ink);
}
.stApp::before {
  content: "";
  position: fixed; top: 0; bottom: 0;
  left: calc(var(--pad) - 28px); width: 2px;
  background: rgba(228, 87, 46, .45);
  pointer-events: none; z-index: 1;
}
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }

[data-testid="stMainBlockContainer"], .block-container {
  width: 100%;
  max-width: 44rem !important;
  margin-left: var(--pad) !important;
  margin-right: auto !important;
  padding: 2.5rem 1rem 9rem 0 !important;
}

/* ---- type ---- */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
  font-family: var(--serif);
  font-size: 1.08rem;
  line-height: 1.65;
  color: var(--ink);
}
h1, h2, h3, h4,
[data-testid="stWidgetLabel"] p,
[data-testid="stCaptionContainer"] p,
.stButton button, [data-testid="stFormSubmitButton"] button {
  font-family: var(--sans) !important;
  color: var(--ink);
}
[data-testid="stWidgetLabel"] p { font-size: .98rem; font-weight: 600; }

/* ---- hero / onboarding ---- */
.wordmark {
  font-family: var(--sans); font-weight: 800; letter-spacing: -.035em;
  color: var(--ink); line-height: 1;
  font-size: clamp(2.6rem, 8vw, 4.2rem); margin: 0 0 .7rem;
}
.wordmark.small { font-size: 1.5rem; margin: 0; letter-spacing: -.02em; }
.lede {
  font-family: var(--serif); font-size: 1.25rem; line-height: 1.5;
  color: var(--ink-soft); max-width: 32rem; margin: 0 0 1.3rem;
}
.checks { list-style: none; padding: 0; margin: 0 0 1.8rem; }
.checks li {
  position: relative; padding-left: 1.6rem; margin: .35rem 0;
  font-family: var(--serif); font-size: 1.08rem; color: var(--ink);
}
.checks li::before {
  content: ""; position: absolute; left: 0; top: .5em;
  width: .72rem; height: .72rem; background: var(--marker);
  border: 1.5px solid var(--ink); border-radius: 2px;
}

[data-testid="stForm"] {
  background: rgba(255, 255, 255, .92);
  border: 1.5px solid var(--ink); border-radius: 16px;
  padding: 1.4rem; box-shadow: 5px 5px 0 var(--ink);
}
[data-baseweb="input"] {
  background: #fff !important; border: 1.5px solid var(--ink) !important; border-radius: 10px !important;
}
[data-baseweb="input"] input { font-family: var(--sans); color: var(--ink); }

/* ---- buttons ---- */
.stButton button, [data-testid="stFormSubmitButton"] button {
  background: #fff; color: var(--ink) !important;
  border: 1.5px solid var(--ink); border-radius: 10px;
  font-weight: 600; padding: .55rem 1.1rem;
  transition: transform .12s ease, box-shadow .12s ease;
}
.stButton button p, [data-testid="stFormSubmitButton"] button p { color: inherit !important; font-family: var(--sans) !important; }
.stButton button:hover, [data-testid="stFormSubmitButton"] button:hover {
  transform: translate(-1px, -1px); box-shadow: 3px 3px 0 var(--ink); border-color: var(--ink);
}
.stButton button:active, [data-testid="stFormSubmitButton"] button:active { transform: none; box-shadow: none; }
button[kind="primary"], button[kind="primaryFormSubmit"],
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"] {
  background: var(--ink) !important; color: #fff !important;
}
button[kind="primary"] p, button[kind="primaryFormSubmit"] p,
[data-testid="stBaseButton-primary"] p, [data-testid="stBaseButton-primaryFormSubmit"] p { color: #fff !important; }
button:focus-visible, input:focus-visible, textarea:focus-visible,
[data-testid="stFileUploaderDropzone"]:focus-visible {
  outline: 3px solid var(--ink) !important; outline-offset: 2px;
}

/* ---- photo drop zone ---- */
[data-testid="stFileUploaderDropzone"] {
  background: rgba(255, 255, 255, .8);
  border: 2px dashed var(--ink-soft); border-radius: 14px;
}
[data-testid="stFileUploaderDropzone"]:hover { border-style: solid; border-color: var(--ink); }

/* ---- the photo, taped into the notebook ---- */
.taped {
  position: relative; display: inline-block; max-width: 100%;
  background: #fff; padding: .6rem .6rem .5rem;
  border: 1.5px solid var(--ink); box-shadow: 4px 4px 0 var(--ink);
  transform: rotate(-2deg); margin: .8rem 0 1.6rem .4rem;
}
.taped::before {
  content: ""; position: absolute; top: -13px; left: 50%;
  width: 84px; height: 24px; margin-left: -42px;
  background: rgba(255, 228, 92, .85); border: 1px solid rgba(27, 42, 91, .25);
  transform: rotate(3deg);
}
.taped img { display: block; max-width: 100%; max-height: 180px; }
.taped span {
  display: block; margin-top: .4rem; font-family: var(--sans);
  font-size: .8rem; color: var(--ink-soft); overflow: hidden;
  text-overflow: ellipsis; white-space: nowrap; max-width: 220px;
}

/* ---- chat ---- */
[data-testid="stChatMessage"] {
  display: flex; background: transparent; border: none; padding: .4rem 0; gap: 0;
}
[data-testid^="stChatMessageAvatar"] { display: none; }
[data-testid="stChatMessageContent"] {
  flex: 1 1 auto; max-width: 100%;
  background: rgba(255, 255, 255, .93);
  border: 1.5px solid var(--ink); border-left-width: 5px;
  border-radius: 4px 16px 16px 16px; padding: 1rem 1.25rem;
  margin: 0;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { justify-content: flex-end; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
  flex: 0 1 auto; max-width: 85%; margin: 0 0 0 auto;
  background: var(--ink); border-left-width: 1.5px; border-radius: 16px 16px 4px 16px;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p { color: #fff; }
[data-testid="stChatMessage"]:not(:has([data-testid="stChatMessageAvatarUser"])) strong {
  background: linear-gradient(transparent 58%, var(--marker) 58%); font-weight: 700;
}
[data-testid="stChatMessage"] [data-testid="stImage"] img {
  border-radius: 8px; border: 1.5px solid rgba(255, 255, 255, .6);
}

/* ---- chat input, pinned at the bottom ---- */
[data-testid="stBottom"], [data-testid="stBottom"] > div, [data-testid="stBottomBlockContainer"] {
  background: transparent !important;
}
[data-testid="stBottomBlockContainer"] {
  max-width: 44rem !important;
  margin-left: var(--pad) !important; margin-right: auto !important;
  padding-left: 0 !important; padding-right: 1rem !important;
}
[data-testid="stChatInput"] {
  background: #fff; border: 1.5px solid var(--ink);
  border-radius: 14px; box-shadow: 4px 4px 0 var(--ink);
}
[data-testid="stChatInput"] > div { background: #fff; border: none; }
[data-testid="stChatInput"] textarea { font-family: var(--sans); color: var(--ink); }

[data-testid="stHeaderActionElements"] { display: none !important; }
[data-testid="stAlert"] { border: 1.5px solid var(--ink); border-radius: 12px; }

[data-testid="stMarkdownContainer"] p.sendto { font-family: var(--sans); font-size: .95rem; color: var(--ink-soft); text-align: right; margin: 0; }
.hint { font-family: var(--serif); font-size: 1.1rem; color: var(--ink-soft); margin: 1.2rem 0; max-width: 30rem; }

/* ---- phones ---- */
@media (max-width: 700px) {
  .stApp::before { display: none; }
  [data-testid="stMainBlockContainer"], .block-container {
    margin-left: auto !important; padding: 1.5rem 1rem 8rem !important;
  }
  [data-testid="stBottomBlockContainer"] { margin-left: auto !important; padding: 0 1rem 1rem !important; }
  [data-testid="stMarkdownContainer"] p.sendto { text-align: left; }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def hero(where):
    """Onboarding header. `where` is the destination in plain words ('email', 'Telegram')."""
    st.markdown(
        '<div class="wordmark">Snap &amp; Study</div>'
        '<p class="lede">Photo of a problem, diagram or notes in. Plain-language explanation out.</p>'
        '<ul class="checks">'
        "<li>Upload a photo and ask about it.</li>"
        "<li>Get the idea explained step by step.</li>"
        f"<li>Send the notes to your {html.escape(where)} so they're saved outside the app.</li>"
        "</ul>",
        unsafe_allow_html=True,
    )


def wordmark_small():
    st.markdown('<div class="wordmark small">Snap &amp; Study</div>', unsafe_allow_html=True)


def sending_to(destination):
    st.markdown(
        f'<p class="sendto">Sending to <b>{html.escape(destination)}</b></p>',
        unsafe_allow_html=True,
    )


def photo_preview(image_bytes, mime, name):
    encoded = base64.b64encode(image_bytes).decode()
    st.markdown(
        f'<div class="taped"><img src="data:{mime};base64,{encoded}" alt="Your uploaded photo">'
        f"<span>{html.escape(name)}</span></div>",
        unsafe_allow_html=True,
    )


def hint(text):
    st.markdown(f'<p class="hint">{html.escape(text)}</p>', unsafe_allow_html=True)
