import json
from dotenv import load_dotenv
from string import Template
from constants import FIELD_TITLE, FIELD_TEXT, FILE_OUTPUT
from exceptions import ApiCreditLimitError, ApiError
import llm

load_dotenv()


SCHEMA = json.dumps({FIELD_TITLE: "string", FIELD_TEXT: "string"})

PROMPT = """You are a helpful German language teacher. Write a short paragraph in
German about the topic "$topic" for a learner at the B1 level.

## Important
- Keep the German level at B1.
- Keep the grammar, case, articles, and word order correct always.
- Always provide the answer in the following JSON schema:
```
$SCHEMA
```
"""

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


def main():
    for i in range(1):
        topic = topics[i]
        try:
            generate_topic(topic)
        except ApiCreditLimitError as e:
            print(f"Out of API credits: {e}")
            break
        except (ApiError, ValueError) as e:
            print(f"Error generating topic '{topic}': {e}")


def generate_topic(topic):
    response = llm.call_model(
        [
            {
                "role": "user",
                "content": Template(PROMPT).substitute(SCHEMA=SCHEMA, topic=topic),
            }
        ],
    )
    save_json_to_file({"response": response}, FILE_OUTPUT)


def save_json_to_file(data: dict, filename: str):
    with open(filename, "a") as f:
        jd = json.dumps(data, ensure_ascii=False)
        f.write(jd + "\n")


if __name__ == "__main__":
    main()
