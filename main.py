import anthropic
import json
from dotenv import load_dotenv
from string import Template
import spacy

load_dotenv()
client = anthropic.Anthropic()
model = "claude-opus-5"

FIELD_TITLE = "title"
FIELD_TEXT = "text"
FIELD_NEW_WORDS = "new_words"
FIELD_WORD = "word"
FIELD_GLOSS = "gloss"

SCHEMA = json.dumps(
    {
        FIELD_TITLE: "string",
        FIELD_TEXT: "string",
        FIELD_NEW_WORDS: [{FIELD_WORD: "string", FIELD_GLOSS: "string"}],
    }
)

PROMPT_V1 = """You are a helpful German languate teacher. Your task is to help me
learn German. You will provide me a short paragraph in German that keeps the
number of new words no more than $WORD_BUDGET words. You can use the words in
the word list as many times as you want in the paragraph.

This word budget applies only to content words,
the function words (articles, pronouns, prepositions, conjunctions, auxiliaries, modals, particles, etc.)
don't count towards the word budget.

The generated paragraph should be about the topic "$topic".

The paragraph should be written in a way that is easy to understand for a German learner at the B1 level.
You will  list every new content word you introduced in the paragraph, along with their English glosses.

## Important
- Keep the German level at B1.
- Keep the Grammer, case, articles, and word order correct always.
- Aalways provide the answer in the following JSON schema:
```
$SCHEMA
```

word list to use: $word_list
"""

PROMPT_REPAIR = """
The German paragraph below uses words I don't know yet.
Rewrite it so that these words no longer appear:
$offending_words

Keep the same topic, the same length, and the same B1 level. Replace each word with something I already know, or rephrase the sentence.
Replace them with words from this list, or with words already in the paragraph:
$word_list

Do not introduce other new content words.

Paragraph to rewrite:
$previous_text

Always answer in the following JSON schema:
$SCHEMA
"""
words_to_generate_from = [
    "Haus",
    "Baum",
    "Katze",
    "Hund",
    "Auto",
    "Straße",
    "Stadt",
    "Land",
    "Freund",
    "Familie",
]

topics = [
    "Ein Tag zu Hause",
    "Mein Haustier",
    "Die Fahrt in die Stadt",
    "Meine Nachbarn",
    "Ein Besuch bei Freunden",
    "Der Garten",
    "Stadt oder Land?",
    "Ein Spaziergang",
    "Das Wochenende mit Familie",
    "Umzug in ein neues Haus",
]


FILE_FREE_WORDS = "free_words.txt"
FILE_KNOWN_WORDS = "known_words.txt"
NEW_WORD_BUDGET = 3


def load_words(path: str) -> set:
    with open(path, "r") as f:
        return {
            stripped
            for line in f.readlines()
            if ((stripped := line.strip()) and not stripped.startswith("#"))
        }


FREE_WORDS = {word.lower() for word in load_words(FILE_FREE_WORDS)}
KNOWN_WORDS = {word.lower() for word in load_words(FILE_KNOWN_WORDS)}

nlp = spacy.load("de_core_news_sm")
import os


def main():
    for i in range(5):
        topic = topics[i]
        try:
            generate_topic(topic)
        except ValueError as e:
            print(f"Error generating topic '{topic}': {e}")
        except anthropic.BadRequestError as e:
            if e.message and "credit balance is too low" in e.message:
                print(f"Buy API credits. Error details: {str(e)}")
                break
            print(str(e))


def generate_topic(topic):
    response = call_model(
        [
            {
                "role": "user",
                "content": Template(PROMPT_V1).substitute(
                    word_list=",".join(words_to_generate_from),
                    SCHEMA=SCHEMA,
                    WORD_BUDGET=NEW_WORD_BUDGET,
                    topic=topic,
                ),
            }
        ],
    )
    attempt = 0
    history = []
    while response.get("new_words_spacy_count") > NEW_WORD_BUDGET and attempt < 3:
        print(
            f"Attempt {attempt}: New words found ({response.get('new_words_spacy_count')}) exceeds the budget ({NEW_WORD_BUDGET}). Retrying..."
        )
        history.append(response)
        response = call_model(
            [
                {
                    "role": "user",
                    "content": Template(PROMPT_REPAIR).substitute(
                        word_list=",".join(words_to_generate_from),
                        offending_words=",".join(response.get("new_words_spacy")),
                        previous_text=response.get("response")
                        .get("content")
                        .get("text"),
                        SCHEMA=SCHEMA,
                    ),
                }
            ]
        )
        attempt += 1

    if response.get("new_words_spacy_count") > NEW_WORD_BUDGET:
        print(
            f"Failed to generate a paragraph within the new word budget after {attempt} attempts."
        )
    print(f"New words found: {response.get('new_words_spacy')}")
    response["attempts"] = attempt
    response["converged"] = response.get("new_words_spacy_count") <= NEW_WORD_BUDGET
    response["history"] = history
    save_json_to_file(response, "output.json")


def call_model(messages: list[dict[str, str]]) -> dict[str, any]:
    message = client.messages.create(
        model=model,
        max_tokens=5000,
        thinking={"type": "adaptive", "display": "summarized"},
        messages=messages,
    )
    try:
        for block in message.content:
            if block.type == "text":
                data = validate_json(extract_json(block.text))
                print(f"{message.role}: {data}")
                to_save = {"role": message.role, "content": data}
                new_words = find_new_words(data.get(FIELD_TEXT), KNOWN_WORDS)
                with_new_words = {
                    "response": to_save,
                    "new_words_spacy": list(new_words),
                    "new_words_spacy_count": len(new_words),
                }

                return with_new_words
    except ValueError as e:
        err = {
            "type": "error",
            "message": str(e),
        }
        raise ValueError(f"Error: {err}")


def find_new_words(text: str | None, known: set[str]) -> set[str]:
    if not text:
        raise ValueError("Text is empty or None")
    new_words = set()
    doc = nlp(text)
    for token in doc:
        if not token.is_punct and not token.is_space:
            lemma = token.lemma_.lower()
            if lemma not in known and lemma not in FREE_WORDS:
                pos = token.pos_
                if pos in ["NOUN", "VERB", "ADJ", "ADV"]:
                    new_words.add(lemma)
    return new_words


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


def save_json_to_file(data: dict, filename: str):
    with open(filename, "a") as f:
        jd = json.dumps(data, ensure_ascii=False)
        f.write(jd + "\n")


if __name__ == "__main__":
    main()
