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

load_dotenv()


class LLMProvider(Enum):
    ANTHROPIC = 0
    PPLX = 1
    GROQ = 2


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
        ]
        return names[self.value]


def ask_llm(
    query: str | list,
    system_prompt: str = "",
    db_file_path: Optional[str] = None,
    provider: LLMProvider = LLMProvider.ANTHROPIC,
    model: Optional[LLMModel] = None,
    max_tokens: int = 4000,
    temperature: float = 0.5,
    seed: Optional[int] = None,
) -> Optional[str]:
    if provider == LLMProvider.ANTHROPIC:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        if model is None:
            model = LLMModel.CLAUDE_HAIKU
        if seed is None:
            seed = 0
        messages = create_messages(query)
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
