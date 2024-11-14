import sys
from pathlib import Path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))

from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
# from llama_index import VectorStoreIndex, SimpleDirectoryReader
# from llama_index.vector_stores import WeaviateVectorStore
#from llama_index.schema import Document
# from llama_index.node_parser import SimpleNodeParser


# from dotenv import dotenv_values
#import weaviate
from pypdf import PdfReader
import streamlit as st
import requests
import time
import json
import plotly.graph_objects as go
from pydantic import create_model
# config = dotenv_values(".env")

# OPENAI_API_KEY = config["OPENAI_API_KEY"]
# AV_API_KEY = config["ALPHA_VANTAGE_API_KEY"]

# OPENAI_API_KEY = st.secrets["openai_api_key"]
# AV_API_KEY = st.secrets["av_api_key"]

AV_API_KEY = st.secrets["av_api_key"]

USER_ID = 'openai'
APP_ID = 'chat-completion'
MODEL_ID = 'GPT-4'
MODEL_VERSION_ID = '4aa760933afa4a33a0e5b4652cfa92fa'

from groq import Groq
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from src.groq_client import get_completion

import os
from pathlib import Path

def ensure_directory_exists(directory_path: str) -> None:
    """Create directory if it doesn't exist"""
    Path(directory_path).mkdir(parents=True, exist_ok=True)

def get_pdf_path(filename: str) -> str:
    """Get the full path for PDF files and ensure directory exists"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Define the pdf directory path
    pdf_dir = project_root / 'pdf'
    
    # Ensure the pdf directory exists
    ensure_directory_exists(pdf_dir)
    
    # Return the full path for the PDF file
    return str(pdf_dir / filename)

def get_model(model_name, api_key):
    client = Groq(api_key=api_key)
    return client

class VectorDB:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.texts = []
        
    def add_texts(self, texts):
        self.texts.extend(texts)
        embeddings = self.model.encode(texts)
        
        # Initialize FAISS index if not exists
        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
        
        # Add vectors to the index
        self.index.add(np.array(embeddings).astype('float32'))
    
    def similarity_search(self, query, k=5):
        # Get the query embedding
        query_embedding = self.model.encode([query])
        
        # Search in the index
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), k)
        
        # Return the most similar texts
        return [self.texts[i] for i in indices[0]]
    
    def save(self, path):
        faiss.write_index(self.index, f"{path}/index.faiss")
        with open(f"{path}/texts.json", 'w') as f:
            json.dump(self.texts, f)
    
    def load(self, path):
        self.index = faiss.read_index(f"{path}/index.faiss")
        with open(f"{path}/texts.json", 'r') as f:
            self.texts = json.load(f)

def create_vector_db(splitted_text):
    db = VectorDB()
    db.add_texts(splitted_text)
    db.save("vector_db")
    return db

def search_vector_db(query, k=5):
    db = VectorDB()
    db.load("vector_db")
    return db.similarity_search(query, k)

def process_pdf(pdfs):
    docs = []
    
    for pdf in pdfs:
        file = PdfReader(pdf)
        text = ""
        for page in file.pages:
            text += str(page.extract_text())
        
        # Split text into chunks
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=2000,
            chunk_overlap=300,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        docs.extend(chunks)

    return docs

# def process_pdf2(pdf):
#     file = PdfReader(pdf)
#     text = ""
#     for page in file.pages:
#         text += str(page.extract_text())
        
#     doc = Document(text=text)
#     return [doc]

def safe_float(value):
        if value == "None" or value == None:
            return "N/A"
        return float(value)

def round_numeric(value, decimal_places=2):
    if isinstance(value, (int, float)):
        return round(value, decimal_places)
    elif isinstance(value, str) and value.replace(".", "", 1).isdigit():
        # Check if the string represents a numeric value
        return round(float(value), decimal_places)
    else:
        return value
    
def format_currency(value):
    if value == "N/A":
        return value
    if value >= 1_000_000_000:  # billion
        return f"${value / 1_000_000_000:.2f} billion"
    elif value >= 1_000_000:  # million
        return f"${value / 1_000_000:.2f} million"
    else:
        return f"${value:.2f}"

def get_total_revenue(symbol):
    time.sleep(3)
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "INCOME_STATEMENT",
        "symbol": symbol,
        "apikey": AV_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    total_revenue = safe_float(data["annualReports"][0]["totalRevenue"])

    return total_revenue

def get_total_debt(symbol):
    time.sleep(3)
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "BALANCE_SHEET",
        "symbol": symbol,
        "apikey": AV_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    short_term = safe_float(data["annualReports"][0]["shortTermDebt"])
    time.sleep(3)
    long_term = safe_float(data["annualReports"][0]["longTermDebt"])

    if short_term == "N/A" or long_term == "N/A":
        return "N/A"
    return short_term + long_term

def generate_pydantic_model(fields_to_include, attributes, base_fields):
    selected_fields = {attr: base_fields[attr] for attr, include in zip(attributes, fields_to_include) if include}
    
    return create_model("DynamicModel", **selected_fields)

def insights(insight_name, type_of_data, data, output_format, api_key):
    with open("prompts/iv2.prompt", "r") as f:
        template = f.read()
    
    formatted_input = template.format(
        insight_name=insight_name,
        type_of_data=type_of_data, 
        inputs=json.dumps(data), 
        output_format=output_format
    )

    return get_completion(formatted_input)

def financial_analysis(data, metric_type):
    prompt = f"Analyze these {metric_type} metrics: {data}"
    return get_completion(prompt)

def format_title(s: str) -> str:
    return ' '.join(word.capitalize() for word in s.split('_'))

def create_time_series_chart(data, type_of_data: str, title: str):
    yaxis_title = format_title(type_of_data)
    fig = go.Figure(data=[go.Scatter(x=data['dates'], y=data[type_of_data], mode='lines+markers')])
    fig.update_layout(yaxis=dict(range=[0, max(data)]))
    fig.update_layout(title=title,
                      xaxis_title='Date',
                      yaxis_title=yaxis_title)
    

    
    return fig

# data = {
#     'dates': ['2022-01-01', '2022-01-02', '2022-01-03', '2022-01-04', '2022-01-05'],
#     'temperature': [22, 24, 23, 22, 21],
#     'humidity': [40, 42, 41, 40, 39]
# }
# # Create a temperature time series chart
# temperature_chart = create_time_series_chart(data, 'temperature')
# temperature_chart.show()

# # Create a humidity time series chart
# humidity_chart = create_time_series_chart(data, 'humidity')
# humidity_chart.show()

import plotly.graph_objects as go

def create_donut_chart(data, type_of_data, hole_size=0.3):

    labels = list(data[type_of_data].keys())
    values = list(data[type_of_data].values())
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=hole_size)])
    fig.update_layout(title=format_title(type_of_data))
    
    return fig

# # Example usage:
# data = {
#     'Oxygen': 4500,
#     'Hydrogen': 2500,
#     'Carbon_Dioxide': 1053,
#     'Nitrogen': 500
# }
# chart = create_donut_chart(data, title="Donut Chart")
# chart.show()

def create_bar_chart(data, type_of_data: str, title: str = None):
    yaxis_title = format_title(type_of_data)
    fig = go.Figure(data=[go.Bar(x=data['dates'], y=data[type_of_data])])
    # fig.update_layout(yaxis=dict(range=[0, max(data[type_of_data])]))
    fig.update_layout(title=format_title(type_of_data),
                      xaxis_title='Date',
                      yaxis_title=yaxis_title)
   
    return fig











