from typing import List

import tiktoken

from discharge_summaries.openai_llm.message import Message


def num_tokens_from_messages_azure_engine(
    messages: List[Message], azure_engine: str, azure_api_version: str
) -> int:
    azure_engine_and_version_to_openai_model = {
        "gpt-35-turbo-2023-07-01-preview": "gpt-3.5-turbo-0613",
        "gpt-4-32k-2023-07-01-preview": "gpt-4-32k-0613",
    }
    try:
        model = azure_engine_and_version_to_openai_model[
            f"{azure_engine}-{azure_api_version}"
        ]
    except KeyError:
        raise NotImplementedError(
            "num_tokens_from_messages() is not implemented for model"
            f" {azure_engine}-{azure_api_version}."
        )
    return _num_tokens_from_messages(messages, model=model)


def _num_tokens_from_messages(messages: List[Message], model: str) -> int:
    """Return the number of tokens used by a list of messages.
    From https://github.com/openai/openai-cookbook/blob/5783656852d507c335955d14875ebc9902f628ef/examples/How_to_count_tokens_with_tiktoken.ipynb # noqa: E501
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print(
            "Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming"
            " gpt-3.5-turbo-0613."
        )
        return _num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print(
            "Warning: gpt-4 may update over time. Returning num tokens assuming"
            " gpt-4-0613."
        )
        return _num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}.
            See https://github.com/openai/openai-python/blob/main/chatml.md for information
            on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.dict().items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens
