import sys
from pathlib import Path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))

import streamlit as st
import os

# Initialize session states first
if "company_overview" not in st.session_state:
    st.session_state.company_overview = None

if "income_statement" not in st.session_state:
    st.session_state.income_statement = None

if "balance_sheet" not in st.session_state:
    st.session_state.balance_sheet = None

if "cash_flow" not in st.session_state:
    st.session_state.cash_flow = None

if "news" not in st.session_state:
    st.session_state.news = None

if "all_outputs" not in st.session_state:
    st.session_state.all_outputs = None

# Initialize insight states
from src.fields2 import inc_stat_attributes, balance_sheet_attributes, cashflow_attributes

for insight in inc_stat_attributes:
    if insight not in st.session_state:
        st.session_state[insight] = None

for insight in balance_sheet_attributes:
    if insight not in st.session_state:
        st.session_state[insight] = None

for insight in cashflow_attributes:
    if insight not in st.session_state:
        st.session_state[insight] = None

# Set page config
st.set_page_config(
    page_title="Finance Metrics Reviews", 
    page_icon=":bar_chart:", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Get API keys from secrets
av_api_key = st.secrets["av_api_key"]
groq_api_key = st.secrets["groq_api_key"]

# Set environment variables
os.environ["AV_API_KEY"] = av_api_key
os.environ["GROQ_API_KEY"] = groq_api_key

st.title(":chart_with_upwards_trend: Finance Metrics Review")
st.info("""
Simply input the ticker symbol of your desired company and hit the 'Generate Insights' button. 
Allow a few moments for the system to compile the data and insights tailored to the selected company. 
Once done, you have the option to browse through these insights directly on the platform or download 
a comprehensive report by selecting 'Generate PDF', followed by 'Download PDF'.
""")

# Import all required modules
from src.income_statement import income_statement
from src.balance_sheet import balance_sheet
from src.cash_flow import cash_flow
from src.news_sentiment import top_news
from src.company_overview import company_overview
from src.utils import round_numeric, format_currency, create_donut_chart, create_bar_chart
from src.pdf_gen import gen_pdf
from src.fields2 import inc_stat, inc_stat_attributes, bal_sheet, balance_sheet_attributes, cashflow, cashflow_attributes
from src.components.chat import chat_interface

# Create two columns for the layout
col1, col2 = st.columns([0.25, 0.75], gap="medium")

with col1:
    st.write("""
    ### Select Insights
    """)
    with st.expander("**Income Statement Insights**", expanded=True):
        revenue_health = st.toggle("Revenue Health")
        operational_efficiency = st.toggle("Operational Efficiency")
        r_and_d_focus = st.toggle("R&D Focus")
        debt_management = st.toggle("Debt Management")
        profit_retention = st.toggle("Profit Retention")

        income_statement_feature_list = [revenue_health, operational_efficiency, r_and_d_focus, debt_management, profit_retention]

    with st.expander("**Balance Sheet Insights**", expanded=True):
        liquidity_position = st.toggle("Liquidity Position")
        assets_efficiency = st.toggle("Operational efficiency")
        capital_structure = st.toggle("Capital Structure")
        inventory_management = st.toggle("Inventory Management")
        overall_solvency = st.toggle("Overall Solvency")

        balance_sheet_feature_list = [liquidity_position, assets_efficiency, capital_structure, inventory_management, overall_solvency]

    with st.expander("**Cash Flow Insights**", expanded=True):
        operational_cash_efficiency = st.toggle("Operational Cash Efficiency")
        investment_capability = st.toggle("Investment Capability")
        financial_flexibility = st.toggle("Financial Flexibility")
        dividend_sustainability = st.toggle("Dividend Sustainability")
        debt_service_capability = st.toggle("Debt Service Capability")

        cash_flow_feature_list = [operational_cash_efficiency, investment_capability, financial_flexibility, dividend_sustainability, debt_service_capability]

with col2:
    # Ticker input section
    st.write("### Enter Company Ticker")
    ticker = st.text_input("Enter ticker symbol", help="Example: AAPL for Apple Inc.")
    
    # Example tickers with better formatting
    st.markdown("""
    **Popular Tickers:**
    - `AAPL` - Apple Inc.
    - `MSFT` - Microsoft Corporation
    - `TSLA` - Tesla Inc.
    - `GOOGL` - Alphabet Inc.
    - `AMZN` - Amazon.com Inc.
    """)

    if ticker:
        if st.button("Generate Insights", key="generate_insights"):
            with st.status("**Generating Insights...**"):
                if not st.session_state.company_overview:
                    st.write("Getting company overview...")
                    st.session_state.company_overview = company_overview(ticker)
                    
                if any(income_statement_feature_list):
                    st.write("Generating income statement insights...")
                    for i, insight in enumerate(inc_stat_attributes):
                        if st.session_state[insight]:
                            income_statement_feature_list[i] = False 

                    response = income_statement(ticker, income_statement_feature_list, groq_api_key)
                    st.session_state.income_statement = response
                    
                    for key, value in response["insights"].items():
                        st.session_state[key] = value
                
                if any(balance_sheet_feature_list):
                    st.write("Generating balance sheet insights...")
                    for i, insight in enumerate(balance_sheet_attributes):
                        if st.session_state[insight]:
                            balance_sheet_feature_list[i] = False

                    response = balance_sheet(ticker, balance_sheet_feature_list, groq_api_key)
                    st.session_state.balance_sheet = response

                    for key, value in response["insights"].items():
                        st.session_state[key] = value
                
                if any(cash_flow_feature_list):
                    st.write("Generating cash flow insights...")
                    for i, insight in enumerate(cashflow_attributes):
                        if st.session_state[insight]:
                            cash_flow_feature_list[i] = False

                    response = cash_flow(ticker, cash_flow_feature_list, groq_api_key)
                    st.session_state.cash_flow = response

                    for key, value in response["insights"].items():
                        st.session_state[key] = value

                if not st.session_state.news:
                    st.write('Getting latest news...')
                    st.session_state.news = top_news(ticker, 10)

                if st.session_state.company_overview and st.session_state.income_statement and st.session_state.balance_sheet and st.session_state.cash_flow and st.session_state.news:
                    st.session_state.all_outputs = True

                if st.session_state.company_overview == None:
                    st.error(f"No Data available for {ticker}")

        # Add tabs section here
        if st.session_state.all_outputs:
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Company Overview", "Income Statement", "Balance Sheet", "Cash Flow", "News Sentiment"])

            if st.session_state.company_overview:
                if "Error" in st.session_state.company_overview:
                    st.error(st.session_state.company_overview["Error Message"])
                else:
                    with tab1:
                        with st.container():
                            st.write("# Company Overview")
                            st.markdown(f"""### {st.session_state.company_overview["Name"]}""")
                            
                            col1, col2, col3 = st.columns(3)
                            col1.markdown("### Symbol:")
                            col1.write(st.session_state.company_overview["Symbol"])
                            col2.markdown("### Exchange:")
                            col2.write(st.session_state.company_overview["Exchange"])
                            col3.markdown("### Currency:")
                            col3.write(st.session_state.company_overview["Currency"])

                            col1, col2, col3 = st.columns(3)
                            col1.markdown("### Sector:")
                            col1.write(st.session_state.company_overview["Sector"])
                            col2.markdown("### Industry:")
                            col2.write(st.session_state.company_overview["Industry"])
                            col3.write()
                            
                            st.markdown("### Description:")
                            st.write(st.session_state.company_overview["Description"])
                            
                            col1, col2, col3 = st.columns(3)
                            col1.markdown("### Country:")
                            col1.write(st.session_state.company_overview["Country"])
                            col2.markdown("### Address:")
                            col2.write(st.session_state.company_overview["Address"])
                            col3.write()

                            col1, col2, col3 = st.columns(3)
                            col1.markdown("### Fiscal Year End:")
                            col1.write(st.session_state.company_overview["FiscalYearEnd"])
                            col2.markdown("### Latest Quarter:")
                            col2.write(st.session_state.company_overview["LatestQuarter"])
                            col3.markdown("### Market Capitalization:")
                            col3.write(format_currency(st.session_state.company_overview["MarketCapitalization"]))

            if st.session_state.income_statement:
                with tab2:
                    st.write("# Income Statement")
                    st.write("## Metrics")
                    
                    with st.container():
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Gross Profit Margin", f"{round_numeric(st.session_state.income_statement['metrics']['gross_profit_margin'], 2)}%")
                        col2.metric("Operating Profit Margin", f"{round_numeric(st.session_state.income_statement['metrics']['operating_profit_margin'], 2)}%")
                        col3.metric("Net Profit Margin", f"{round_numeric(st.session_state.income_statement['metrics']['net_profit_margin'], 2)}%")
                        col1.metric("Cost Efficiency", f"{round_numeric(st.session_state.income_statement['metrics']['cost_efficiency'], 2)}%")
                        col2.metric("SG&A Efficiency", f"{round_numeric(st.session_state.income_statement['metrics']['sg_and_a_efficiency'], 2)}%")
                        col3.metric("Interest Coverage Ratio", round_numeric(st.session_state.income_statement['metrics']['interest_coverage_ratio'], 2))
                    
                    st.write("## Insights")
                    # Revenue Health
                    if revenue_health and st.session_state["revenue_health"]:
                        st.write("### Revenue Health")
                        insight_text = st.session_state["revenue_health"]
                        if isinstance(insight_text, dict):
                            insight_text = insight_text.get('revenue_health', '')
                        st.markdown(insight_text.replace('$', '\\$'))
                        st.write(create_bar_chart(st.session_state.income_statement["chart_data"], "total_revenue", "Revenue Growth"))
                    
                    # Operational Efficiency
                    if operational_efficiency and st.session_state["operational_efficiency"]:
                        st.write("### Operational Efficiency")
                        insight_text = st.session_state["operational_efficiency"]
                        if isinstance(insight_text, dict):
                            insight_text = insight_text.get('operational_efficiency', '')
                        st.markdown(insight_text.replace('$', '\\$'))
                    
                    # R&D Focus
                    if r_and_d_focus and st.session_state["r_and_d_focus"]:
                        st.write("### R&D Focus")
                        insight_text = st.session_state["r_and_d_focus"]
                        if isinstance(insight_text, dict):
                            insight_text = insight_text.get('r_and_d_focus', '')
                        st.markdown(insight_text.replace('$', '\\$'))
                    
                    # Debt Management
                    if debt_management and st.session_state["debt_management"]:
                        st.write("### Debt Management")
                        insight_text = st.session_state["debt_management"]
                        if isinstance(insight_text, dict):
                            insight_text = insight_text.get('debt_management', '')
                        st.markdown(insight_text.replace('$', '\\$'))
                        st.write(create_bar_chart(st.session_state.income_statement["chart_data"], "interest_expense", "Interest Expense Trend"))
                    
                    # Profit Retention
                    if profit_retention and st.session_state["profit_retention"]:
                        st.write("### Profit Retention")
                        insight_text = st.session_state["profit_retention"]
                        if isinstance(insight_text, dict):
                            insight_text = insight_text.get('profit_retention', '')
                        st.markdown(insight_text.replace('$', '\\$'))
                        st.write(create_bar_chart(st.session_state.income_statement["chart_data"], "net_income", "Net Income Trend"))

            if st.session_state.balance_sheet:
                with tab3:
                    st.write("# Balance Sheet")
                    st.write("## Metrics")

                    with st.container():
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Current Ratio", round_numeric(st.session_state.balance_sheet['metrics']['current_ratio'], 2))
                        col2.metric("Debt to Equity Ratio", f"{round_numeric(st.session_state.balance_sheet['metrics']['debt_to_equity_ratio'], 2)}x")
                        col3.metric("Quick Ratio", round_numeric(st.session_state.balance_sheet['metrics']['quick_ratio'], 2))
                        col1.metric("Asset Turnover", f"{round_numeric(st.session_state.balance_sheet['metrics']['asset_turnover'], 2)}x")
                        col2.metric("Equity Multiplier", f"{round_numeric(st.session_state.balance_sheet['metrics']['equity_multiplier'], 2)}x")

                    st.write("## Insights")
                    # Liquidity Position
                    if liquidity_position and st.session_state["liquidity_position"]:
                        st.write("### Liquidity Position")
                        insight_text = st.session_state["liquidity_position"]
                        if isinstance(insight_text, dict):
                            insight_text = insight_text.get('liquidity_position', '')
                        st.markdown(insight_text.replace('$', '\\$'))
                        st.write(create_donut_chart(st.session_state.balance_sheet["chart_data"], "asset_composition"))
                    
                    # Assets Efficiency
                    if assets_efficiency and st.session_state["assets_efficiency"]:
                        st.write("### Assets Efficiency")
                        insight_text = st.session_state["assets_efficiency"]
                        if isinstance(insight_text, dict):
                            insight_text = insight_text.get('assets_efficiency', '')
                        st.markdown(insight_text.replace('$', '\\$'))
                    
                    # Capital Structure
                    if capital_structure and st.session_state["capital_structure"]:
                        st.write("### Capital Structure")
                        insight_text = st.session_state["capital_structure"]
                        if isinstance(insight_text, dict):
                            insight_text = insight_text.get('capital_structure', '')
                        st.markdown(insight_text.replace('$', '\\$'))
                        st.write(create_donut_chart(st.session_state.balance_sheet["chart_data"], "liabilities_composition"))
                    
                    # Inventory Management
                    if inventory_management and st.session_state["inventory_management"]:
                        st.write("### Inventory Management")
                        insight_text = st.session_state["inventory_management"]
                        if isinstance(insight_text, dict):
                            insight_text = insight_text.get('inventory_management', '')
                        st.markdown(insight_text.replace('$', '\\$'))
                    
                    # Overall Solvency
                    if overall_solvency and st.session_state["overall_solvency"]:
                        st.write("### Overall Solvency")
                        insight_text = st.session_state["overall_solvency"]
                        if isinstance(insight_text, dict):
                            insight_text = insight_text.get('overall_solvency', '')
                        st.markdown(insight_text.replace('$', '\\$'))
                        st.write(create_donut_chart(st.session_state.balance_sheet["chart_data"], "debt_structure"))

            if st.session_state.cash_flow:
                with tab4:
                    st.write("# Cash Flow")
                    st.write("## Metrics")

                    with st.container():
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Operating Cash Flow Margin", f"{round_numeric(st.session_state.cash_flow['metrics']['operating_cash_flow_margin'], 2)}%")
                        col2.metric("Capital Expenditure Coverage Ratio", f"{round_numeric(st.session_state.cash_flow['metrics']['capital_expenditure_coverage_ratio'], 2)}x")
                        col3.metric("Dividend Coverage Ratio", f"{round_numeric(st.session_state.cash_flow['metrics']['dividend_coverage_ratio'], 2)}x")
                        col1.metric("Cash Flow to Debt Ratio", f"{round_numeric(st.session_state.cash_flow['metrics']['cash_flow_to_debt_ratio'], 2)}x")
                        col2.metric("Free Cash Flow", format_currency(st.session_state.cash_flow['metrics']['free_cash_flow']).replace('$', '\\$'))

                    st.write("## Insights")
                    # Operational Cash Efficiency
                    if operational_cash_efficiency and st.session_state["operational_cash_efficiency"]:
                        st.write("### Operational Cash Efficiency")
                        insight_text = st.session_state["operational_cash_efficiency"]
                        if isinstance(insight_text, dict):
                            insight_text = insight_text.get('operational_cash_efficiency', '')
                        st.markdown(insight_text.replace('$', '\\$'))
                        st.write(create_bar_chart(st.session_state.cash_flow["chart_data"], "operating_cash_flow", "Operating Cash Flow Trend"))
                    
                    # Investment Capability
                    if investment_capability and st.session_state["investment_capability"]:
                        st.write("### Investment Capability")
                        insight_text = st.session_state["investment_capability"]
                        if isinstance(insight_text, dict):
                            insight_text = insight_text.get('investment_capability', '')
                        st.markdown(insight_text.replace('$', '\\$'))
                        st.write(create_bar_chart(st.session_state.cash_flow["chart_data"], "cash_flow_from_investment", "Investment Cash Flow Trend"))
                    
                    # Financial Flexibility
                    if financial_flexibility and st.session_state["financial_flexibility"]:
                        st.write("### Financial Flexibility")
                        insight_text = st.session_state["financial_flexibility"]
                        if isinstance(insight_text, dict):
                            insight_text = insight_text.get('financial_flexibility', '')
                        st.markdown(insight_text.replace('$', '\\$'))
                        st.write(create_bar_chart(st.session_state.cash_flow["chart_data"], "cash_flow_from_financing", "Financing Cash Flow Trend"))
                    
                    # Dividend Sustainability
                    if dividend_sustainability and st.session_state["dividend_sustainability"]:
                        st.write("### Dividend Sustainability")
                        insight_text = st.session_state["dividend_sustainability"]
                        if isinstance(insight_text, dict):
                            insight_text = insight_text.get('dividend_sustainability', '')
                        st.markdown(insight_text.replace('$', '\\$'))
                    
                    # Debt Service Capability
                    if debt_service_capability and st.session_state["debt_service_capability"]:
                        st.write("### Debt Service Capability")
                        insight_text = st.session_state["debt_service_capability"]
                        if isinstance(insight_text, dict):
                            insight_text = insight_text.get('debt_service_capability', '')
                        st.markdown(insight_text.replace('$', '\\$'))

            if st.session_state.news:
                with tab5:
                    st.markdown("## Top News")
                    column_config = {
                        "title": st.column_config.Column(
                            "Title",
                            width="large",
                        ),
                        "url": st.column_config.LinkColumn(
                            "Link",
                            width="medium",
                        ),
                        "authors": st.column_config.ListColumn(
                            "Authors",
                            width="medium"
                        ),
                        "topics": st.column_config.ListColumn(
                            "Topics",
                            width="large"
                        ),
                        "sentiment_score": st.column_config.ProgressColumn(
                            "Sentiment Score",
                            min_value=-0.5,
                            max_value=0.5
                        ),
                        "sentiment_label": st.column_config.Column(
                            "Sentiment Label"
                        )
                    }

                    st.metric("Mean Sentiment Score",
                             value=round_numeric(st.session_state.news["mean_sentiment_score"]),
                             delta=st.session_state.news["mean_sentiment_class"])

                    st.dataframe(st.session_state.news["news"], column_config=column_config)

# Add chat interface
if st.session_state.all_outputs:
    st.markdown("---")
    st.subheader("💬 Chat with Your Analysis")
    
    chat_context = {
        "Company Overview": st.session_state.company_overview,
        "Income Statement": st.session_state.income_statement,
        "Balance Sheet": st.session_state.balance_sheet,
        "Cash Flow": st.session_state.cash_flow,
        "News": st.session_state.news
    }
    
    chat_interface(chat_context)

# Rest of your existing code for processing and displaying results...

