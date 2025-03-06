from typing import Any, Optional, List
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.runnables import RunnableConfig


class DeepSeekR1ChatOllama(ChatOllama):
    """Custom chat model for DeepSeek-R1."""

    def invoke(
            self,
            input: List[BaseMessage],
            config: Optional[RunnableConfig] = None,
            **kwargs: Any,
    ) -> AIMessage:
        """Invoke the chat model with DeepSeek-R1 specific processing."""
        org_ai_message = super().invoke(input, config, **kwargs)
        org_content = org_ai_message.content

        # Extract reasoning content and main content
        org_content = str(org_ai_message.content)
        if "</think>" in org_content:
            parts = org_content.split("</think>")
            reasoning_content = parts[0].replace("<think>", "").strip()
            content = parts[1].strip()

            # Remove JSON Response tag if present
            if "**JSON Response:**" in content:
                content = content.split("**JSON Response:**")[-1].strip()

            # Create AIMessage with extra attributes
            message = AIMessage(content=content)
            setattr(message, "reasoning_content", reasoning_content)
            return message

        return AIMessage(content=org_ai_message.content)

    async def ainvoke(
            self,
            input: List[BaseMessage],
            config: Optional[RunnableConfig] = None,
            **kwargs: Any,
    ) -> AIMessage:
        """Async invoke the chat model with DeepSeek-R1 specific processing."""
        org_ai_message = await super().ainvoke(input, config, **kwargs)
        org_content = org_ai_message.content

        # Extract reasoning content and main content
        org_content = str(org_ai_message.content)
        if "</think>" in org_content:
            parts = org_content.split("</think>")
            reasoning_content = parts[0].replace("<think>", "").strip()
            content = parts[1].strip()

            # Remove JSON Response tag if present
            if "**JSON Response:**" in content:
                content = content.split("**JSON Response:**")[-1].strip()

            # Create AIMessage with extra attributes
            message = AIMessage(content=content)
            setattr(message, "reasoning_content", reasoning_content)
            return message

        return AIMessage(content=org_ai_message.content)
