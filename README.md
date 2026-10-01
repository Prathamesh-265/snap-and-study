# Snap & Study

1. `pip install -r requirements.txt`
2. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`, fill it in
3. Write `SYSTEM_PROMPT` and `SUMMARY_PROMPT` in `prompts.py`
4. `streamlit run app.py`

Swap send tool: set `ACTION_TOOL` to `email`, `telegram`, or `whatsapp` in secrets.

For WhatsApp, use the Twilio Sandbox while testing. From the phone that should
receive messages, send the Sandbox join phrase to the Twilio WhatsApp number
shown in the Twilio Console. The recipient must join before this app can deliver
messages. A successful API request is initially `queued`; check the Twilio
Console message log for the final delivery status.
