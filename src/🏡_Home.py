import sys
from pathlib import Path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))

import streamlit as st

st.set_page_config(page_title="FinSights AI", page_icon=":robot_face:", layout="wide")

# Title with AI emphasis
st.title(":robot_face: FinSights AI \n\n **AI-Powered Financial Insights**")

#st.balloons()

# About the App
st.header("About FinSights AI")
st.info("""
FinSights AI is a cutting-edge financial analysis platform that harnesses the power of artificial intelligence 
to deliver comprehensive financial insights. Our platform combines advanced AI capabilities with robust 
financial data analysis to provide you with actionable intelligence.

The application offers two powerful AI-driven features:

1. **AI Finance Metrics Review** 📊
   - AI-powered analysis of company financial metrics
   - Intelligent insights about income statements, balance sheets, and cash flows
   - Dynamic charts and visualizations
   - Interactive AI chat assistant for deeper analysis

2. **AI Annual Report Analyzer** 🗂️
   - Advanced PDF processing with AI
   - Intelligent extraction of key insights
   - AI-powered section analysis
   - Context-aware chat functionality

Key AI Features:
- State-of-the-art LLM analysis using Groq API
- AI-driven data visualization
- Real-time financial metrics processing
- Intelligent document understanding
- Context-aware AI chat interface
- Deep financial insights powered by AI
""")

# How to Use
st.header("Getting Started")
st.success("""
1. **AI Finance Metrics Review**:
   - Simply enter a company's ticker symbol
   - Let our AI analyze the metrics you select
   - Receive AI-generated insights and visualizations
   - Engage with our AI assistant for detailed analysis

2. **AI Annual Report Analyzer**:
   - Upload any company's annual report PDF
   - Our AI processes and understands the document
   - Get AI-powered structured analysis
   - Use the intelligent chat interface for deep insights
""")

# Creators Section
st.header("Meet the Team")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Jinav Gala")
    st.markdown("""
    - Roll Number: A023
    - [LinkedIn](https://www.linkedin.com/in/jinav-gala)
    - [GitHub](https://github.com/jinav22)
    - Email: jinavgala@gmail.com
    """)

with col2:
    st.subheader("Tina Narsinghani")
    st.markdown("""
    - Roll Number: A040
    - [LinkedIn](https://www.linkedin.com/in/tina-narsinghani/)
    - [GitHub](https://github.com/TinaHN)
    - Email: tinanmims23@gmail.com
    """)

# Footer
st.markdown("---")
st.markdown("### 🤖 Powered by Advanced AI | Built with Streamlit and Groq")
st.markdown("#### © 2024 FinSights AI - Transforming Financial Analysis with Artificial Intelligence")

