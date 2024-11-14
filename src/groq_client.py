from groq import Groq
import streamlit as st

def get_groq_client():
    return Groq(api_key=st.secrets["groq_api_key"])

def get_completion(prompt: str, model: str = "llama-3.2-90b-text-preview") -> str:
    client = get_groq_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response.choices[0].message.content 