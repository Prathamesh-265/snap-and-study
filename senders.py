import asyncio
import smtplib
from email.mime.text import MIMEText

import streamlit as st


def send_email(to_address, text):
    message = MIMEText(text)
    message["Subject"] = "Your Snap & Study notes"
    message["From"] = st.secrets["GMAIL_ADDRESS"]
    message["To"] = to_address

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
        server.login(st.secrets["GMAIL_ADDRESS"], st.secrets["GMAIL_APP_PASSWORD"])
        server.send_message(message)


def send_telegram(chat_id, text):
    from telegram import Bot

    bot = Bot(token=st.secrets["TELEGRAM_BOT_TOKEN"])
    asyncio.run(
        bot.send_message(
            chat_id=chat_id,
            text=text,
            read_timeout=10,
            write_timeout=10,
            connect_timeout=10,
            pool_timeout=10,
        )
    )

def _whatsapp(number):
    """Twilio needs the 'whatsapp:' prefix on both From and To."""
    number = number.strip().replace(" ", "").replace("-", "")
    return number if number.startswith("whatsapp:") else f"whatsapp:{number}"


def send_whatsapp(number, text):
    from twilio.rest import Client
    from twilio.http.http_client import TwilioHttpClient

    client = Client(
        st.secrets["TWILIO_ACCOUNT_SID"],
        st.secrets["TWILIO_AUTH_TOKEN"],
        http_client=TwilioHttpClient(timeout=10),
    )
    message = client.messages.create(
        from_=_whatsapp(st.secrets["TWILIO_WHATSAPP_FROM"]),
        to=_whatsapp(number),
        body=text[:1600],  # WhatsApp message limit
    )
    return {"sid": message.sid, "status": message.status}


# Everything the UI needs to know about each tool lives here.
TOOLS = {
    "email": {
        "where": "email",
        "label": "Your email address",
        "placeholder": "you@gmail.com",
        "hint": "Your study notes get sent here. Nothing else.",
        "button": "Send to my email",
        "valid": lambda v: "@" in v and "." in v.split("@")[-1],
        "send": send_email,
    },
    "telegram": {
        "where": "Telegram",
        "label": "Your Telegram chat_id",
        "placeholder": "123456789",
        "hint": "Message your bot once first, or it can't reach you.",
        "button": "Send to Telegram",
        "valid": lambda v: v.lstrip("-").isdigit(),
        "send": send_telegram,
    },
    "whatsapp": {
        "where": "WhatsApp",
        "label": "Your WhatsApp number",
        "placeholder": "+919876543210",
        "hint": "Include the country code. In the Twilio sandbox, join it from this number first.",
        "button": "Send to WhatsApp",
        "valid": lambda v: v.startswith("+") and v[1:].isdigit() and 8 <= len(v) <= 16,
        "send": send_whatsapp,
    },
}