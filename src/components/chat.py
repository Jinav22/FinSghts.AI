import streamlit as st
from src.groq_client import get_completion

def format_currency_for_display(text):
    """Replace $ with \$ to prevent LaTeX interpretation"""
    return text.replace("$", "\\$") if isinstance(text, str) else text

def init_chat_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def display_chat_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            formatted_content = format_currency_for_display(message["content"])
            st.markdown(formatted_content)

def create_chat_prompt(context, question):
    return f"""
    Based on the following context, please answer the question.
    Provide a clear, concise, and informative response.
    When mentioning dollar amounts, use USD or dollars instead of $ symbol.
    
    Context:
    {context}
    
    Question:
    {question}
    
    Remember to:
    - Use specific data and examples from the context when relevant
    - Maintain a professional tone
    - Focus on accuracy and clarity
    - Format currency as 'USD' or 'dollars' instead of '$'
    """

def format_context(context_data):
    """Format context data, handling currency symbols"""
    formatted_context = ""
    if isinstance(context_data, dict):
        for key, value in context_data.items():
            formatted_value = str(value).replace("$", "USD ")
            formatted_context += f"\n{key}:\n{formatted_value}\n"
    else:
        formatted_context = str(context_data).replace("$", "USD ")
    return formatted_context

def chat_interface(context_data):
    init_chat_state()
    
    # Display chat messages
    display_chat_messages()
    
    # Chat input
    if prompt := st.chat_input("Ask a question about the analysis..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Format context with proper currency handling
                context = format_context(context_data)
                
                # Get response from Groq
                full_prompt = create_chat_prompt(context, prompt)
                response = get_completion(full_prompt)
                
                # Format response for display
                formatted_response = format_currency_for_display(response)
                st.markdown(formatted_response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response}) 