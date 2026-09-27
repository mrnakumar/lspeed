import json
from dotenv import load_dotenv
from string import Template
from constants import *
import llm
import german
import os

load_dotenv()


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


NEW_WORD_BUDGET = 3

FILE_FREE_WORDS = "free_words.txt"
FILE_KNOWN_WORDS = "known_words.txt"
FREE_WORDS = german.load_words(FILE_FREE_WORDS)
KNOWN_WORDS = german.load_words(FILE_KNOWN_WORDS)


def main():
    for i in range(1):
        topic = topics[i]
        try:
            generate_topic(topic)
        except ValueError as e:
            print(f"Error generating topic '{topic}': {e}")


def generate_topic(topic):
    response = llm.call_model(
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
    response = with_new_words(response)
    while response.get("new_words_spacy_count") > NEW_WORD_BUDGET and attempt < 3:
        print(
            f"Attempt {attempt}: New words found ({response.get('new_words_spacy_count')}) exceeds the budget ({NEW_WORD_BUDGET}). Retrying..."
        )
        history.append(response)
        response = llm.call_model(
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
        response = with_new_words(response)
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


def with_new_words(response: dict[str, any]) -> dict[str, any]:
    content = response["content"]
    new_words = german.find_new_words(content.get(FIELD_TEXT), KNOWN_WORDS, FREE_WORDS)
    with_new_words = {
        "response": response,
        "new_words_spacy": list(new_words),
        "new_words_spacy_count": len(new_words),
    }
    return with_new_words


def save_json_to_file(data: dict, filename: str):
    with open(filename, "a") as f:
        jd = json.dumps(data, ensure_ascii=False)
        f.write(jd + "\n")


if __name__ == "__main__":
    main()
