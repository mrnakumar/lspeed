import anthropic
import json
from dotenv import load_dotenv
from string import Template

load_dotenv()
client = anthropic.Anthropic()
model="claude-opus-5"

FIELD_TITLE="title"
FIELD_TEXT="text"
FIELD_NEW_WORDS="new_words"
FIELD_WORD="word"
FIELD_GLOSS="gloss"

SCHEMA= json.dumps(
     {
          FIELD_TITLE: "string",
          FIELD_TEXT: "string",
          FIELD_NEW_WORDS: [{FIELD_WORD: "string", FIELD_GLOSS: "string"}]
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
You will  list every new content word you introduced in the paragraph, with their English glosses,
along with their English glosses.

## Important
- Keep the German level at B1.
- Keep the Grammer, case, articles, and word order correct always.
- Aalways provide the answer in the following JSON schema:
```
$SCHEMA
```

word list to use: $word_list
"""

word_list = ["Haus", "Baum", "Katze", "Hund", "Auto", "Straße", "Stadt", "Land", "Freund", "Familie"]
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
    for i in range(10):
      topic = topics[i]
      beHappy(topic)

def beHappy(topic: str):
  message =  client.messages.create(
    model=model,
    max_tokens = 5000,

    thinking ={"type": "adaptive", "display": "summarized"},
    messages = [
     {
       "role" : "user",
       "content": Template(PROMPT_V1).substitute(word_list=",".join(word_list),
                                                 SCHEMA=SCHEMA, WORD_BUDGET = len(word_list),
                                                 topic = topic)
     }
     ],
  )
#   print(message.model_dump_json(indent=2))
  try:
   for block in message.content:
         if block.type == "text":
               data = validate_json(extract_json(block.text))
               print(f'{message.role}: {data}')
               to_save = {
                    "role": message.role,
                    "content": data
               }
               save_json_to_file(to_save, "output.json")
  except ValueError as e:
                     err = {
                        "type": "error",
                        "message": str(e),
                     }
                     print(f'Error: {err}')


def extract_json(text : str):
   i = text.find("{")
   j = text.rfind("}")
   if i == -1 or j == -1:
      raise ValueError(f"No JSON found in the text : {text}")
   relevant_text = text[i : j+ 1]
   return json.loads(relevant_text)

def validate_json(obj: dict):
     if not obj[FIELD_TITLE] :
         raise ValueError(f"Missing '{FIELD_TITLE}' field in the JSON object")
     if not obj[FIELD_TEXT] :
         raise ValueError(f"Missing '{FIELD_TEXT}' field in the JSON object")
     if not obj[FIELD_NEW_WORDS] :
         raise ValueError(f"Missing '{FIELD_NEW_WORDS}' field in the JSON object")
     NEW_WORDS = obj[FIELD_NEW_WORDS]
     if not isinstance(NEW_WORDS, list):
         print(f"NEW_WORDS: {NEW_WORDS}")
         raise ValueError(f"'{FIELD_NEW_WORDS}' field must be a list")
     for e in NEW_WORDS:
         if not isinstance(e, dict):
             raise ValueError(f"Each element in '{FIELD_NEW_WORDS}' must be a dictionary")
         if not e[FIELD_WORD] :
             raise ValueError(f"Missing '{FIELD_WORD}' field in the new word object")
         if not e[FIELD_GLOSS] :
             raise ValueError(f"Missing '{FIELD_GLOSS}' field in the new word object")

     return {
        FIELD_TITLE: obj[FIELD_TITLE],
        FIELD_TEXT: obj[FIELD_TEXT],
        FIELD_NEW_WORDS: obj[FIELD_NEW_WORDS]
     }

def save_json_to_file(data: dict, filename: str):
    with open(filename, "a") as f:
         jd = json.dumps(data, ensure_ascii=False)
         f.write(jd + "\n")

if __name__ == "__main__":
    main()
