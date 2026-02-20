import streamlit as st
import telebot
import requests
from groq import Groq
import threading
import os

GROQ_API_KEY = st.secrets["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"]
TELEGRAM_BOT_TOKEN = st.secrets["8320724315:AAGN0Zh5aMpotmLSYfo_v6WFiR_RF_xkNMk"]
GIST_RAW_URL = st.secrets["https://gist.githubusercontent.com/RahmatRumon/45b4dcd54ab117c618d70c70ea84c102/raw/school_data.json"]

groq_client = Groq(api_key=GROQ_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def fetch_school_data():
    try:
        response = requests.get(GIST_RAW_URL)
        return response.text
    except Exception as e:
        return f"Data fetch error: {e}"

def get_ai_response(user_query):
    school_info = fetch_school_data()
    
    system_prompt = f"তুমি একটি স্কুল অ্যাসিস্ট্যান্ট বট। নিচের তথ্যের ভিত্তিতে উত্তর দাও: {school_info}"
    
    completion = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        temperature=0.7,
        max_tokens=1024,
    )
    return completion.choices[0].message.content

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "স্বাগতম! আমি আপনার স্কুলের তথ্য দিয়ে সাহায্য করতে পারি। আপনার প্রশ্ন লিখুন।")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    response = get_ai_response(message.text)
    bot.reply_to(message, response)

def run_telegram_bot():
    bot.infinity_polling()

def main():
    st.set_page_config(page_title="School Chatbot", page_icon="🏫")
    st.title("🏫 আমি স্কুল ইনফরমেশন চ্যাটবট মুন")
    st.write("যেকোনো প্রশ্ন জিজ্ঞেস করুন আমাদের স্কুল সম্পর্কে।")

    if 'bot_started' not in st.session_state:
        thread = threading.Thread(target=run_telegram_bot)
        thread.daemon = True
        thread.start()
        st.session_state['bot_started'] = True

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("আপনার প্রশ্ন লিখুন..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = get_ai_response(prompt)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()