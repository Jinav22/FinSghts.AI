from groq import Groq
import streamlit as st

def analyze_financial_metrics(data, metric_type):
    client = Groq(api_key=st.secrets["groq_api_key"])
    
    prompt = f"""
    Analyze the following {metric_type} metrics and provide insights:
    {data}
    
    Please provide:
    1. Key observations
    2. Potential implications
    3. Areas of concern (if any)
    4. Recommendations
    """
    
    response = client.chat.completions.create(
        model="llama-3.2-90b-text-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )
    
    return response.choices[0].message.content 