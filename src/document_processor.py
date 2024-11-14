from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Optional
from pypdf import PdfReader
import json
from src.groq_client import get_completion
import streamlit as st

class DocumentProcessor:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', chunk_size: int = 500):
        self.model = SentenceTransformer(model_name)
        self.chunk_size = chunk_size
        self.index = None
        self.chunks = []

    def process_pdf(self, pdf_file) -> List[str]:
        """Extract text from PDF and split into chunks"""
        try:
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            
            # Split into smaller chunks with overlap
            words = text.split()
            chunks = []
            current_chunk = []
            word_count = 0
            
            for word in words:
                current_chunk.append(word)
                word_count += 1
                
                if word_count >= self.chunk_size:
                    chunks.append(' '.join(current_chunk))
                    # Keep last 50 words for context overlap
                    current_chunk = current_chunk[-50:]
                    word_count = len(current_chunk)
            
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                
            self.chunks = chunks
            return chunks
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return []

    def create_index(self):
        """Create FAISS index from chunks"""
        try:
            if not self.chunks:
                raise ValueError("No chunks available to create index")
                
            embeddings = self.model.encode(self.chunks)
            dimension = embeddings.shape[1]
            
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(np.array(embeddings).astype('float32'))
            return True
        except Exception as e:
            st.error(f"Error creating index: {str(e)}")
            return False

    def search(self, query: str, k: int = 3) -> List[str]:
        """Search for relevant chunks"""
        if not self.index:
            raise ValueError("Index not created. Please process document first.")
            
        query_vector = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), k)
        
        return [self.chunks[i] for i in indices[0]]

    def query(self, question: str) -> str:
        """Query the document with a question"""
        try:
            relevant_chunks = self.search(question)
            context = "\n".join(relevant_chunks)
            
            prompt = f"""
            Based on the following context from an annual report, please answer the question.
            Structure your response in the following format:

            1. Key Findings:
            - Main point 1
            - Main point 2
            - Main point 3

            2. Detailed Analysis:
            [Provide a detailed analysis broken down into clear paragraphs]

            3. Summary:
            [A brief conclusion of the findings]

            Context:
            {context}

            Question:
            {question}

            Remember to:
            - Use clear, concise language
            - Break down complex information into digestible points
            - Provide specific examples or data when available
            - Maintain a professional tone
            """
            
            response = get_completion(prompt)
            
            # Format the response for better display
            formatted_response = {
                "structured_analysis": {
                    "key_findings": response.split("1. Key Findings:")[1].split("2. Detailed Analysis:")[0].strip(),
                    "detailed_analysis": response.split("2. Detailed Analysis:")[1].split("3. Summary:")[0].strip(),
                    "summary": response.split("3. Summary:")[1].strip()
                }
            }
            
            return formatted_response
            
        except Exception as e:
            st.error(f"Error querying document: {str(e)}")
            return {
                "structured_analysis": {
                    "error": "Unable to process query at this time.",
                    "details": str(e)
                }
            } 