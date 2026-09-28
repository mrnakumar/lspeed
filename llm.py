import anthropic
import json
from constants import FIELD_TITLE, FIELD_TEXT, FIELD_WORD, FIELD_NEW_WORDS, FIELD_GLOSS
from dotenv import load_dotenv
from exceptions import ApiError, ApiCreditLimitError

# FIXME: also loaded in main.py, load it only once
load_dotenv()

client = anthropic.Anthropic()
model = "claude-opus-5"


def call_model(messages: list[dict[str, str]]) -> dict[str, any]:
    try:
        message = client.messages.create(
            model=model,
            max_tokens=5000,
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
    NEW_WORDS = obj.get(FIELD_NEW_WORDS)
    if not isinstance(NEW_WORDS, list):
        print(f"NEW_WORDS: {NEW_WORDS}")
        raise ValueError(f"'{FIELD_NEW_WORDS}' field must be a list")
    for e in NEW_WORDS:
        if not isinstance(e, dict):
            raise ValueError(
                f"Each element in '{FIELD_NEW_WORDS}' must be a dictionary"
            )
        if not e.get(FIELD_WORD):
            raise ValueError(f"Missing '{FIELD_WORD}' field in the new word object")
        if not e.get(FIELD_GLOSS):
            raise ValueError(f"Missing '{FIELD_GLOSS}' field in the new word object")

    return {
        FIELD_TITLE: obj[FIELD_TITLE],
        FIELD_TEXT: obj[FIELD_TEXT],
        FIELD_NEW_WORDS: obj[FIELD_NEW_WORDS],
    }
