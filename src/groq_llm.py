from typing import Any, List, Optional, Dict, Iterator, AsyncGenerator, AsyncIterator
from groq import Groq
import streamlit as st
from llama_index.llms import LLMMetadata, CompletionResponse, CompletionResponseGen, LLM
from llama_index.llms.base import ChatMessage, ChatResponse, ChatResponseGen
import asyncio

class GroqLLM(LLM):
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.2-90b-text-preview"):
        self.client = Groq(api_key=api_key or st.secrets["groq_api_key"])
        self.model = model
        self._metadata = LLMMetadata(
            model_name=model,
            model_type="groq",
            context_window=4096,
            max_tokens=1024,
            is_chat_model=True,
            is_function_calling_model=False
        )

    @property
    def metadata(self) -> LLMMetadata:
        return self._metadata

    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return CompletionResponse(text=response.choices[0].message.content)

    def stream_complete(self, prompt: str, **kwargs) -> Iterator[CompletionResponse]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield CompletionResponse(text=chunk.choices[0].delta.content)

    def chat(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages
        )
        return ChatResponse(message=ChatMessage(
            role="assistant",
            content=response.choices[0].message.content
        ))

    def stream_chat(
        self, messages: List[ChatMessage], **kwargs
    ) -> Iterator[ChatResponse]:
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield ChatResponse(message=ChatMessage(
                    role="assistant",
                    content=chunk.choices[0].delta.content
                ))

    async def acomplete(self, prompt: str, **kwargs) -> CompletionResponse:
        return self.complete(prompt, **kwargs)

    async def astream_complete(self, prompt: str, **kwargs) -> AsyncIterator[CompletionResponse]:
        for response in self.stream_complete(prompt, **kwargs):
            yield response

    async def achat(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        return self.chat(messages, **kwargs)

    async def astream_chat(
        self, messages: List[ChatMessage], **kwargs
    ) -> AsyncIterator[ChatResponse]:
        for response in self.stream_chat(messages, **kwargs):
            yield response