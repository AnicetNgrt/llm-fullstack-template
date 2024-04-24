import csv
import datetime
import hashlib
import logging
import os
from typing import Optional
from enum import Enum
import anthropic
from dotenv import load_dotenv
from openai import OpenAI
from groq import Groq
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage as MistralChatMessage

load_dotenv()


class LLMProvider(Enum):
    ANTHROPIC = 0
    PPLX = 1
    GROQ = 2
    MISTRAL = 3
    OPENAI = 4


class LLMModel(Enum):
    CLAUDE_HAIKU = 0
    CLAUDE_SONNET = 1
    CLAUDE_OPUS = 2
    PPLX_LLAMA3_70 = 3
    PPLX_LLAMA3_8 = 4
    PPLX_MIXTRAL_8x22 = 5
    PPLX_SONAR_MD_ONLINE = 6
    PPLX_SONAR_SM_ONLINE = 7
    GROQ_LLAMA3_70 = 8
    GROQ_LLAMA3_8 = 9
    MISTRAL_SMALL = 10
    MISTRAL_MEDIUM = 11
    MISTRAL_LARGE = 12
    MISTRAL_MIXTRAL_8x22 = 13
    OPENAI_GPT_4_TURBO = 14
    OPENAI_GPT_4_TURBO_PREVIEW = 15
    OPENAI_GPT_4_VISION_PREVIEW = 16
    OPENAI_GPT_3_5_TURBO = 17

    def __str__(self):
        """Return the string representation of the LLMModel."""
        names = [
            "claude-3-haiku-20240307",
            "claude-3-sonnet-20240229",
            "claude-3-opus-20240229",
            "llama-3-70b-instruct",
            "llama-3-8b-instruct",
            "mixtral-8x22b-instruct",
            "sonar-medium-online",
            "sonar-small-online",
            "llama3-70b-8192",
            "llama3-8b-8192",
            "mistral-small-latest",
            "mistral-medium-latest",
            "mistral-large-latest",
            "open-mixtral-8x22b",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-4-vision-preview",
            "gpt-3.5-turbo"
        ]
        return names[self.value]

    def is_coherent_with_provider(self, provider: LLMProvider) -> bool:
        """Check if the LLMModel is coherent with the LLMProvider."""
        if provider == LLMProvider.PPLX:
            return self in [LLMModel.PPLX_LLAMA3_70, LLMModel.PPLX_LLAMA3_8, LLMModel.PPLX_MIXTRAL_8x22, LLMModel.PPLX_SONAR_MD_ONLINE, LLMModel.PPLX_SONAR_SM_ONLINE]
        if provider == LLMProvider.GROQ:
            return self in [LLMModel.GROQ_LLAMA3_70, LLMModel.GROQ_LLAMA3_8]
        if provider == LLMProvider.MISTRAL:
            return self in [LLMModel.MISTRAL_SMALL, LLMModel.MISTRAL_MEDIUM, LLMModel.MISTRAL_LARGE, LLMModel.MISTRAL_MIXTRAL_8x22]
        if provider == LLMProvider.OPENAI:
            return self in [LLMModel.OPENAI_GPT_4_TURBO, LLMModel.OPENAI_GPT_4_TURBO_PREVIEW, LLMModel.OPENAI_GPT_4_VISION_PREVIEW, LLMModel.OPENAI_GPT_3_5_TURBO]
        return True


def ask_llm(
    query: str | list,
    system_prompt: str = "",
    db_file_path: Optional[str] = None,
    provider: LLMProvider = LLMProvider.ANTHROPIC,
    model: LLMModel = LLMModel.CLAUDE_HAIKU,
    max_tokens: int = 4000,
    temperature: float = 0.5,
    json_mode: bool = False,
    seed: Optional[int] = None,
) -> Optional[str]:
    """Query LLMs.

    Please note that not all arguments work with all providers and models, especially system_prompt, max_tokens, json_mode, and temperature.

    Use db_file_path to cache the queries in a CSV file.

    Advanced example usages:

    ```python
    ask_llm("What is the capital of France?", provider=LLMProvider.PPLX, model=LLMModel.PPLX_LLAMA3_8, max_tokens=1000, temperature=0.3)
    ```

    ```
    ask_llm(
        [
            "What is the capital of France?",
            previous_llm_answer,
            "Give me more details about it",
        ],
        provider=LLMProvider.GROQ,
        model=LLMModel.GROQ_LLAMA3_70
    )
    ```

    ```python
    ask_llm("What is the capital of France?", provider=LLMProvider.PPLX, model=LLMModel.PPLX_SONAR_MD_ONLINE)
    ```

    Multimodal with Claude 3 example usage:

    ```python
    ask_llm(
        [
            user([
                picture("path/to/la_eiffel_tour.png"),
                text("What is the building in this picture?"),
            ]),
            assistant(text(previous_llm_answer)),
            user([
                picture("path/to/la_eiffel_tour.png"),
                text("Give me its construction year"),
            ]),
            assistant(text("Its construction year is:")), // pre-prompt supported by Claude 3
        ],
        provider=LLMProvider.ANTHROPIC,
        model=LLMModel.CLAUDE_SONNET
    )
    ```

    JSON mode with Mistral:

    ```python
    ask_llm(
        "Give the names of the 20 largest cities in France in order of popularity. Answer in JSON format with a top-level key 'cities' which is a list of strings.",
        provider=LLMProvider.MISTRAL,
        model=LLMModel.MISTRAL_LARGE,
        json_mode=True
    )
    ```

    Tool use with Mistral:

    1. checkout https://github.com/mistralai/client-python/blob/main/examples/function_calling.py
    2. prompt manually using the mistralai client
    ```
    """

    assert model.is_coherent_with_provider(provider), f"Model {model} is not coherent with provider {provider}"

    if provider == LLMProvider.ANTHROPIC:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        if model is None:
            model = LLMModel.CLAUDE_HAIKU
        if seed is None:
            seed = 0
        messages = create_messages(query)
    elif provider == LLMProvider.MISTRAL:
        api_key = os.environ["MISTRAL_API_KEY"]
        client = MistralClient(api_key=api_key)
        messages = [MistralChatMessage(role="user", content=query)]
        if isinstance(query, list):
            messages = [
                MistralChatMessage(role="user" if i % 2 == 0 else "assistant", content=content)
                for i, content in enumerate(query)
            ]
        if len(system_prompt) > 0:
            messages = [MistralChatMessage(role="system", content=system_prompt)] + messages
    elif provider == LLMProvider.OPENAI:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if model is None:
            model = LLMModel.OPENAI_GPT_3_5_TURBO
        messages = create_openai_messages(query, system_prompt)
    else:
        if provider == LLMProvider.PPLX:
            llm = OpenAI(
                api_key=os.getenv("PERPLEXITY_API_KEY"),
                base_url="https://api.perplexity.ai",
            )
        else:  # provider == LLMProvider.GROQ
            llm = Groq(api_key=os.getenv("GROQ_API_KEY"))
        if model is None:
            model = (
                LLMModel.PPLX_LLAMA3_70
                if provider == LLMProvider.PPLX
                else LLMModel.GROQ_LLAMA3_70
            )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]
        if isinstance(query, list):
            messages = [{"role": "system", "content": system_prompt}]
            for i, message in enumerate(query):
                if i % 2 == 0:
                    messages.append({"role": "user", "content": message})
                else:
                    messages.append({"role": "assistant", "content": message})

    params_str = str(
        {
            "seed": seed,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
    )
    prompt_hash = None
    params_hash = None
    if db_file_path is not None:
        # Generate hashes for the prompt and params
        prompt_hash = generate_hash(str(system_prompt + query))
        params_hash = generate_hash(params_str)
        # Check if the exact same call exists in the CSV file
        response = read_from_csv(db_file_path, prompt_hash, params_hash)
        if response is not None:
            return response

    try:
        if provider == LLMProvider.ANTHROPIC:
            message = client.messages.create(
                model=str(model),
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
                system=system_prompt,
            )
            response = message.content[0].text
        elif provider == LLMProvider.MISTRAL:
            response = client.chat(
                model=str(model),
                messages=messages,
                response_format={"type": "json_object"} if json_mode else None,
                max_tokens=max_tokens,
                temperature=temperature
            )
            response = response.choices[0].message.content
        elif provider == LLMProvider.OPENAI:
            response = client.chat.completions.create(
                model=str(model),
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            response = response.choices[0].message.content
        else:
            response = llm.chat.completions.create(
                model=str(model),
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            response = response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error asking LLM: {e}")
        return None

    if db_file_path is not None:
        # Write the new entry to the CSV file
        timestamp = int(datetime.datetime.now().timestamp())
        row = [
            timestamp,
            str(model),
            prompt_hash,
            params_hash,
            params_str,
            str(system_prompt + "\n\n---\n\n" + query),
            response,
            1,
        ]
        write_to_csv(db_file_path, row)

    return response


def create_messages(query):
    messages = [{"role": "user", "content": [{"type": "text", "text": query}]}]
    if isinstance(query, list):
        messages = []
        for i, message in enumerate(query):
            content = []
            if isinstance(message, str):
                content.append(text(message))
                role = "user" if i % 2 == 0 else "assistant"
                messages.append({"role": role, "content": content})
            else:
                for element in message["content"]:
                    if element["type"] == "image":
                        # open the image file, deduct media type and base64 encode
                        with open(element["path"], "rb") as image:
                            if element["path"].endswith(".jpeg") or element[
                                "path"
                            ].endswith(".jpg"):
                                media_type = "image/jpeg"
                            elif element["path"].endswith(".png"):
                                media_type = "image/png"
                            content.append(
                                {
                                    "type": "image",
                                    "media_type": media_type,
                                    "data": image.read().encode("base64"),
                                }
                            )
                    else:
                        content.append(element)
                messages.append({"role": message["role"], "content": content})
    return messages


def create_openai_messages(query, system_prompt):
    messages = [{"role": "user", "content": query}]
    if isinstance(query, list):
        messages = []
        for i, message in enumerate(query):
            if isinstance(message, str):
                role = "user" if i % 2 == 0 else "assistant"
                messages.append({"role": role, "content": message})
            else:
                content = ""
                for element in message["content"]:
                    if element["type"] == "image":
                        with open(element["path"], "rb") as image:
                            if element["path"].endswith(".jpeg") or element[
                                "path"
                            ].endswith(".jpg"):
                                media_type = "image/jpeg"
                            elif element["path"].endswith(".png"):
                                media_type = "image/png"
                            content += f"<image_url>data:{media_type};base64,{image.read().decode('utf-8')}</image_url>"
                    else:
                        content += element["text"]
                messages.append({"role": message["role"], "content": content})
    if len(system_prompt) > 0:
        messages = [{"role": "system", "content": system_prompt}] + messages
    return messages


def text(text: str):
    return {"type": "text", "text": text}


def picture(path: str):
    return {"type": "image", "path": path}


def user(content: list | dict):
    if isinstance(content, list):
        return {"role": "user", "content": content}
    elif isinstance(content, dict):
        return {"role": "user", "content": [content]}


def assistant(content: list | dict):
    if isinstance(content, list):
        return {"role": "assistant", "content": content}
    elif isinstance(content, dict):
        return {"role": "assistant", "content": [content]}


def write_to_csv(db_file_path: str, row: list):
    """Write a row to the CSV file."""
    with open(db_file_path, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(row)


def read_from_csv(
    db_file_path: str, prompt_hash: str, params_hash: str
) -> Optional[int]:
    """Read the `answer` from the CSV file for the given `prompt_hash` and `params_hash`."""
    answer = None
    with open(db_file_path, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["prompt_hash"] == prompt_hash and row["params_hash"] == params_hash:
                answer = row["answer"]
                break
    return answer


def generate_hash(input_str: str) -> str:
    """Generate a hash for the input string."""
    return hashlib.sha256(input_str.encode()).hexdigest()


def parse_one_answer(response: str) -> str | None:
    find = response.removeprefix("\n").removesuffix("\n").strip().split("</answer>")[0]
    if find == "":
        return None
    return find


def wrap_prompt(prompt: str | list, assistant_prefix: str):
    messages = []
    if isinstance(prompt, list):
        messages = prompt
    else:
        messages = [{"role": "user", "content": {"type": "text", "text": prompt}}]
    return messages
