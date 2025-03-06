from enum import Enum

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from deepseek_r1_chat_ollama import DeepSeekR1ChatOllama


class LLMVendor(Enum):
    OPENAI = 1
    DEEPSEEK = 2

class LLMSelector:
    @staticmethod
    def get_llm(vendor: LLMVendor, model_name: str, without_thinking_output: bool = False):
        if vendor == LLMVendor.OPENAI:
            return LLMSelector.get_llm_instance_openai(model_name=model_name)
        elif vendor == LLMVendor.DEEPSEEK:
            return LLMSelector.get_llm_instance_deepseek(model_name=model_name, without_thinking_output=without_thinking_output)
        else:
            print(f"not found vendor:{vendor}")
            return None

    @staticmethod
    def get_llm_instance_openai(model_name: str) -> ChatOpenAI:
        return ChatOpenAI(model=model_name, temperature=0)

    @staticmethod
    def get_llm_instance_deepseek(model_name: str, without_thinking_output: bool = False) -> DeepSeekR1ChatOllama | ChatOllama:
        if without_thinking_output:
            return DeepSeekR1ChatOllama(
                model=model_name,
                temperature=0.0,
                num_ctx=32000,
                base_url="http://127.0.0.1:11434",
            )
        else:
            return ChatOllama(
                model=model_name,
                temperature=0.0,
                num_ctx=32000,
                base_url="http://127.0.0.1:11434",
            )