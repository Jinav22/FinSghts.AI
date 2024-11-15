# 💸 FinSight: 
**Financial Insights at Your Fingertips**

Finsight is a cutting-edge finance AI assistant tailored to meet the needs of portfolio managers, investors, and finance enthusiasts. By leveraging `Groq` and financial data, Finsight provides deep insights and actionable summaries about a company, aiding in more informed investment decisions.

## Features
📊 **Finance Metrics Overview**:
- Dive deep into core financial metrics extracted from the income statement, balance sheet, and cash flow.
- Stay updated with the top news sentiment surrounding the company for the current year, ensuring you're always in the loop.
- These are the different sections:
  - **Company Overview**: Get a quick overview of the company.
  - **Income Statement**: Understand the company's revenue and expenses.
  - **Balance Sheet**: Get a grasp on the company's assets, liabilities, and shareholders' equity.
  - **Cash Flow**: Understand the company's cash flow from operating, investing, and financing activities.
  - **News Sentiment**: Stay updated with the top news sentiment surrounding the company for the current year.

📄 **Annual Report Analyzer**:
- Simply upload a company's annual report.
- Finsight will then provide comprehensive insights into:
  - **Fiscal Year Highlights**: Major achievements, milestones, and financial highlights.
  - **Strategy Outlook and Future Direction**: Understand the company's strategic plans and anticipated future trajectory.
  - **Risk Management**: Insight into the company's risk assessment, potential challenges, and mitigation strategies.
  - **Innovation and R&D**: Get a grasp on the company's commitment to innovation and its R&D endeavors.

## Tech Stack 
- **Streamlit**: Powers the frontend, providing a seamless user interface.
- **Groq**: High-performance LLM API for generating insights and analysis.
- **Alpha Vantage**: The go-to API service for fetching the most recent financial data about companies.
- **Sentence Transformers & FAISS**: Powers the document processing and similarity search capabilities.

## How to Use

### **Local Setup**:

1. **Clone the Repository**:
```bash
git clone <placeholder>
cd finsight
```

2. **Set Up a Virtual Environment** (Optional but Recommended):
```bash
# For macOS and Linux:
python3 -m venv venv

# For Windows:
python -m venv venv
```

3. **Activate the Virtual Environment**:
```bash
# For macOS and Linux:
source venv/bin/activate

# For Windows:
.\venv\Scripts\activate
```

4. **Install Required Dependencies**:
```bash
pip install -r requirements.txt
```

5. **Set up the Environment Variables**:
```bash
# create directory
mkdir .streamlit

# create toml file
touch .streamlit/secrets.toml
```

You can get your API keys here: [AlphaVantage](https://www.alphavantage.co/support/#api-key), [Groq](https://console.groq.com/)

```bash
# add the following API keys to .streamlit/secrets.toml
av_api_key = "ALPHA_VANTAGE_API_KEY"
groq_api_key = "GROQ_API_KEY"
eod_api_key = "EOD_API_KEY"  # For ticker symbol lookup
```

6. **Run Finsight**:
```bash
streamlit run src/🏡_Home.py
```

After running the command, Streamlit will provide a local URL (usually `http://localhost:8501/`) which you can open in your web browser to access Finsight.

## Creators

### Jinav Gala
- Roll Number: A023
- [LinkedIn](https://www.linkedin.com/in/jinav-gala)
- [GitHub](https://github.com/jinav22)
- Email: jinavgala@gmail.com

### Tina Narsinghani
- Roll Number: A040
- [LinkedIn](https://www.linkedin.com/in/tina-narsinghani/)
- [GitHub](https://github.com/TinaHN)
- Email: tinanmims23@gmail.com

---
🤖 Powered by Advanced AI | Built with Streamlit and Groq

© 2024 FinSights AI - Transforming Financial Analysis with Artificial Intelligence
