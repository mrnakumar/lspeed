import anthropic
from dotenv import load_dotenv
from string import Template

load_dotenv()
client = anthropic.Anthropic()
model="claude-opus-5"

PROMPT_V1 = """You are a helpful German languate teacher. Your task is to help me
learn German. Given a word list, you will provide me a short paragraph in German that only uses
the words in the list plus a maximum of 10 new words that are not in the word list.
Keep the German level at B1.
Important: always provide the answer in the following JSON schema:
```
{
"title": "string",
"text": "string",
"new_words": [ {"word": "string", "gloss": "string"}]
}```

word list to use: $word_list
"""

word_list = ["Haus", "Baum", "Katze", "Hund", "Auto", "Straße", "Stadt", "Land", "Freund", "Familie"]
def main():
    beHappy()

import anthropic
def beHappy():
  message =  client.messages.create(
    model=model,
    max_tokens = 5000,

    thinking ={"type": "adaptive", "display": "summarized"},
    messages = [
     {
       "role" : "user",
       "content": Template(PROMPT_V1).substitute(word_list=word_list)
     }
     ],
  )
#   print(message.model_dump_json(indent=2))

  for block in message.content:
       if block.type == "text":
            try:
              print(f'{message.role}: {extract_json(block.text)}')
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
   return text[i : j+ 1]


if __name__ == "__main__":
    main()
