from abc import abstractmethod

import openai

from llm_discharge_summaries.openai_llm.message import Message, Role


class ChatModel:
    @abstractmethod
    def query(self, messages: list[Message]) -> Message:
        pass

    @abstractmethod
    async def aquery(self, messages: list[Message]) -> Message:
        pass


class AzureOpenAIChatModel(ChatModel):
    def __init__(
        self,
        api_version,
        api_base,
        api_key,
        engine,
        temperature=0,
        timeout=20,
    ):
        super().__init__()
        openai.api_type = "azure"
        openai.api_version = api_version
        openai.api_base = api_base
        openai.api_key = api_key

        self.engine = engine
        self.temperature = temperature
        self.timeout = timeout

    def query(self, messages: list[Message]) -> Message:
        response = openai.ChatCompletion.create(
            engine=self.engine,
            messages=[message.dict() for message in messages],
            temperature=self.temperature,
            timeout=self.timeout,
        )
        return Message(
            role=Role.ASSISTANT,
            content=(response["choices"][0]["message"]["content"]),
        )

    async def aquery(self, messages: list[Message]) -> Message:
        response = await openai.ChatCompletion.acreate(
            engine=self.engine,
            messages=[message.dict() for message in messages],
            temperature=self.temperature,
            timeout=self.timeout,
        )
        return Message(
            role=Role.ASSISTANT,
            content=(response["choices"][0]["message"]["content"]),
        )
