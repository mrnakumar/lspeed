import anthropic
import json
import time

from pydantic import BaseModel
from constants import FIELD_TITLE, FIELD_TEXT
from dotenv import load_dotenv
from exceptions import ApiError, ApiCreditLimitError

# FIXME: also loaded in main.py, load it only once
load_dotenv()

client = anthropic.Anthropic()
model = "claude-opus-5"
max_tokens = 5000


def call_model(messages: list[dict[str, str]]) -> dict[str, any]:
    try:
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            thinking={"type": "adaptive", "display": "summarized"},
            messages=messages,
        )
        for block in message.content:
            if block.type == "text":
                data = validate_json(extract_json(block.text))
                return {"role": message.role, "content": data}
        raise ValueError("No text block in response")
    except anthropic.BadRequestError as e:
        if e.message and "credit balance is too low" in e.message:
            raise ApiCreditLimitError(str(e)) from e
        raise ApiError(str(e)) from e


def parse[T: BaseModel](
    messages: list[dict], output_type: type[T], model: str = model
) -> T:
    start = time.perf_counter()
    try:
        response = client.messages.parse(
            model=model,
            max_tokens=max_tokens,
            thinking={"type": "adaptive", "display": "summarized"},
            messages=messages,
            output_format=output_type,
        )
    except anthropic.BadRequestError as e:
        if e.message and "credit balance is too low" in e.message:
            raise ApiCreditLimitError(str(e)) from e
        raise ApiError(str(e)) from e
    except anthropic.APIError as e:
        raise ApiError(str(e)) from e
    print(f"{model} took {time.perf_counter() - start:.1f}s")
    if response.stop_reason != "end_turn" or response.parsed_output is None:
        raise ApiError(
            f"No {output_type.__name__} returned (stop_reason: {response.stop_reason})"
        )
    return response.parsed_output


def extract_json(text: str):
    i = text.find("{")
    j = text.rfind("}")
    if i == -1 or j == -1:
        raise ValueError(f"No JSON found in the text : {text}")
    relevant_text = text[i : j + 1]
    return json.loads(relevant_text)


def validate_json(obj: dict):
    if not obj.get(FIELD_TITLE):
        raise ValueError(f"Missing '{FIELD_TITLE}' field in the JSON object")
    if not obj.get(FIELD_TEXT):
        raise ValueError(f"Missing '{FIELD_TEXT}' field in the JSON object")
    return {
        FIELD_TITLE: obj[FIELD_TITLE],
        FIELD_TEXT: obj[FIELD_TEXT],
    }
