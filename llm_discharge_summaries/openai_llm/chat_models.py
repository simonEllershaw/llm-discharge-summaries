from abc import abstractmethod

import openai
from openai.error import TryAgain

from llm_discharge_summaries.openai_llm.message import Message, Role


class ChatModel:
    @abstractmethod
    def query(self, messages: list[Message], num_retries=0) -> Message:
        pass

    @abstractmethod
    async def aquery(self, messages: list[Message], num_retries=0) -> Message:
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
        max_retries=3,
    ):
        super().__init__()
        openai.api_type = "azure"
        openai.api_version = api_version
        openai.api_base = api_base
        openai.api_key = api_key

        self.engine = engine
        self.temperature = temperature
        self.timeout = timeout
        self.max_retries = max_retries

    def query(self, messages: list[Message], num_retries=0, **kwargs) -> Message:
        try:
            response = openai.ChatCompletion.create(
                engine=self.engine,
                messages=[message.dict() for message in messages],
                temperature=self.temperature,
                timeout=self.timeout,
                **kwargs
            )
        except TryAgain as e:
            if num_retries < self.max_retries:
                return self.query(messages, num_retries + 1, **kwargs)
            else:
                raise e
        return Message(
            role=Role.ASSISTANT,
            content=(response["choices"][0]["message"]["content"]),
        )

    async def aquery(self, messages: list[Message], num_retries=0) -> Message:
        try:
            response = await openai.ChatCompletion.acreate(
                engine=self.engine,
                messages=[message.dict() for message in messages],
                temperature=self.temperature,
                timeout=self.timeout,
            )
        except TryAgain as e:
            if num_retries < self.max_retries:
                return self.query(messages, num_retries + 1)
            else:
                raise e
        return Message(
            role=Role.ASSISTANT,
            content=(response["choices"][0]["message"]["content"]),
        )
