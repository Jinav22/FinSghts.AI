import sys
from pathlib import Path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))

from src.document_processor import DocumentProcessor
from src.fields2 import (
    fiscal_year, fiscal_year_attributes,
    strat_outlook, strat_outlook_attributes,
    risk_management, risk_management_attributes,
    innovation, innovation_attributes
)
from src.components.chat import chat_interface

import streamlit as st
import time

st.set_page_config(
    page_title="Annual Report Analyzer", 
    page_icon=":card_index_dividers:", 
    initial_sidebar_state="expanded", 
    layout="wide"
)

st.title(":card_index_dividers: Annual Report Analyzer")
st.info("""
Begin by uploading the annual report of your chosen company in PDF format. 
Afterward, click on 'Process PDF'. Once the document has been processed, 
tap on 'Analyze Report' to generate insights.
""")

def initialize_session_state():
    if "processor" not in st.session_state:
        st.session_state.processor = None
    if "processed" not in st.session_state:
        st.session_state.processed = False
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    if "results" not in st.session_state:
        st.session_state.results = {}

def process_document(pdf):
    try:
        with st.spinner("Processing document..."):
            processor = DocumentProcessor()
            chunks = processor.process_pdf(pdf)
            if chunks:
                success = processor.create_index()
                if success:
                    st.session_state.processor = processor
                    st.session_state.processed = True
                    st.success("Document processed successfully!")
                    return True
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
    return False

def analyze_report():
    try:
        processor = st.session_state.processor
        results = {}
        
        with st.spinner("Analyzing report..."):
            sections = {
                "Fiscal Year Highlights": (fiscal_year_attributes, 1),
                "Strategy & Outlook": (strat_outlook_attributes, 2),
                "Risk Management": (risk_management_attributes, 3),
                "Innovation & R&D": (innovation_attributes, 4)
            }
            
            progress_bar = st.progress(0)
            total_sections = len(sections)
            
            for idx, (section_name, (attributes, section_num)) in enumerate(sections.items()):
                section_results = {}
                st.write(f"Analyzing {section_name}...")
                
                for field in attributes:
                    formatted_field = field.replace('_', ' ').title()
                    query = f"What are the {formatted_field} in the {section_name} section?"
                    response = processor.query(query)
                    section_results[formatted_field] = response
                
                results[section_name] = section_results
                progress_bar.progress((idx + 1) / total_sections)
        
        st.session_state.results = results
        st.session_state.analysis_complete = True
        st.success("Analysis complete!")
        
    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")

def format_display_value(value):
    """Format values for display, escaping dollar signs"""
    if isinstance(value, str):
        return value.replace("$", "\\$")
    return value

def display_results():
    if st.session_state.analysis_complete:
        st.write("## Analysis Results")
        
        for section, insights in st.session_state.results.items():
            with st.container():
                st.subheader(section)
                st.markdown("---")
                
                for field, response in insights.items():
                    with st.expander(f"📊 {field}"):
                        try:
                            if isinstance(response, dict) and "structured_analysis" in response:
                                analysis = response["structured_analysis"]
                                
                                # Key Findings
                                st.markdown("### Key Findings")
                                st.markdown(format_display_value(analysis["key_findings"]))
                                
                                # Detailed Analysis
                                st.markdown("### Detailed Analysis")
                                st.markdown(format_display_value(analysis["detailed_analysis"]))
                                
                                # Summary
                                st.markdown("### Summary")
                                st.markdown(format_display_value(analysis["summary"]))
                            else:
                                # Handle plain text responses
                                st.markdown(format_display_value(str(response)))
                                
                        except Exception as e:
                            st.error(f"Error displaying results: {str(e)}")
                
                st.markdown("<br>", unsafe_allow_html=True)

def main():
    initialize_session_state()
    
    # File upload section
    with st.sidebar:
        st.write("## Upload Document")
        pdf_file = st.file_uploader(
            "Upload Annual Report (PDF)", 
            type="pdf",
            help="Upload a PDF file of the annual report you want to analyze."
        )
        
        if pdf_file:
            if st.button("Process Document", key="process_doc"):
                process_document(pdf_file)
        
        if st.session_state.processed:
            if st.button("Analyze Report", key="analyze_report"):
                analyze_report()
        
        # Example reports info
        st.markdown("---")
        st.write("## Example Reports")
        st.info("""
        You can try these example reports:
        - [Apple Inc.](https://s2.q4cdn.com/470004039/files/doc_financials/2022/q4/_10-K-2022-(As-Filed).pdf)
        - [Microsoft Corporation](https://microsoft.gcs-web.com/static-files/07cf3c30-cfc3-4567-b20f-f4b0f0bd5087)
        - [Tesla Inc.](https://digitalassets.tesla.com/tesla-contents/image/upload/IR/TSLA-Q4-2022-Update)
        """)
    
    # Main content area
    if st.session_state.processed:
        st.success("✅ Document is processed and ready for analysis")
    
    # Display results
    display_results()
    
    # Add chat interface after results display
    if st.session_state.analysis_complete:
        st.markdown("---")
        st.subheader("💬 Chat with Your Document")
        
        # Create context from analysis results and original document
        chat_context = {
            "Analysis Results": st.session_state.results,
            "Document Chunks": st.session_state.processor.chunks if st.session_state.processor else []
        }
        
        chat_interface(chat_context)

if __name__ == "__main__":
    main()
