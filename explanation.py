from pydantic import BaseModel
from typing import Literal
from string import Template


class Explanation(BaseModel):
    case: Literal["Nom", "Acc", "Dat", "Gen"] | None
    gender: Literal["Masc", "Fem", "Neut"] | None
    number: Literal["Sing", "Plur"] | None
    governed_by: str | None
    rule: str | None
    explanation: str


PROMPT_EXPLAIN = """You are a German grammar teacher. A learner is reading the German text
below and has tapped the word in square brackets. Explain the grammar of that word,
as it is used in this text.

The learner is at B1 level: they know a lot of vocabulary but find grammar hard.
Explain why the word has this form here.

Fill in the fields as follows:
- case, gender, number: the word's case, gender and number in this text. Use null
  for any that don't apply to this word. For example, prepositions, verbs, adverbs
  and conjunctions have no case, and plural words have no gender.
- governed_by: the word in the text that causes this form, such as the preposition
  or verb that decides the case. Use null if nothing in the text does.
- rule: the general grammar rule behind the form, in one sentence, for example
  "mit always takes the dative". Use null only if no rule applies.
- explanation: one or two sentences in English explaining why the word has this
  form in this text. For a word without case, explain the effect it has instead,
  for example that weil sends the verb to the end of the clause.

Text:
$marked_text
"""
