import streamlit as st
import requests

# Backend URL
BASE_URL = "http://127.0.0.1:8000"

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "You are a travel assistant. Let's plan a one-day trip for the user."}
    ]

st.title("One-Day Tour Planning Assistant")
st.write("Chat with your assistant to plan your trip.")

# Input field for user message
user_input = st.text_input("You:", key="user_input", placeholder="Type your message here...")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # Asking response from backend
    try:
        response = requests.post(f"{BASE_URL}/interact/", json={"message": user_input})
        if response.status_code == 200:
            reply = response.json()["response"]  
            st.session_state["messages"].append({"role": "system", "content": reply})
        else:
            st.session_state["messages"].append({"role": "system", "content": "I'm sorry, something went wrong."})
    except Exception as e:
        st.session_state["messages"].append({"role": "system", "content": f"Error: {str(e)}"})

# Showing chat in reverse order
st.write("---")
for message in reversed(st.session_state["messages"]):
    if message["role"] == "user":
        st.markdown(f"**You:** {message['content']}")
    else:
        st.markdown(f"**Assistant:** {message['content']}")

st.write("\n\n")

if st.button("Clear Chat"):
    st.session_state["messages"] = [
        {"role": "system", "content": "You are a travel assistant. Let's plan a one-day trip for the user."}
    ]
