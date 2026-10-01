import time

import streamlit as st
from google import genai
from google.genai import types

import prompts

# Tried in order. Free quota is counted per model, so when the first one runs out
# for the day, the next one takes over.
MODELS = ["gemini-3.8-flash", "gemini-3.1-flash-lite"]


@st.cache_resource
def _client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


def _to_contents(history):
    """Turn our simple message dicts into Gemini Content objects."""
    contents = []
    for m in history:
        parts = []
        if m.get("image"):
            parts.append(types.Part.from_bytes(data=m["image"], mime_type=m["mime"]))
        parts.append(types.Part.from_text(text=m["text"]))
        contents.append(types.Content(role=m["role"], parts=parts))
    return contents


def _generate(contents):
    last_error = None
    for model in MODELS:
        for attempt in range(4):
            try:
                response = _client().models.generate_content(
                    model=model,
                    contents=contents,
                    config=types.GenerateContentConfig(system_instruction=prompts.SYSTEM_PROMPT),
                )
                return response.text
            except Exception as e:
                last_error = e
                code = getattr(e, "code", None)
                if code not in (429, 503):
                    raise
                if code == 429 and "PerDay" in str(e):
                    break  # daily quota for this model is gone: waiting won't help, try the next model
                time.sleep(2**attempt)  # 503 / per-minute limit: wait 1s, 2s, 4s, 8s and retry
    raise last_error


def ask(history):
    """Next chat reply, given the full conversation so far."""
    return _generate(_to_contents(history))


def summarize(history):
    """Text to send out: the conversation plus SUMMARY_PROMPT as a final turn."""
    closing = types.Content(
        role="user", parts=[types.Part.from_text(text=prompts.SUMMARY_PROMPT)]
    )
    return _generate(_to_contents(history) + [closing])