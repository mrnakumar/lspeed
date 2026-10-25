import spacy


nlp = spacy.load("de_core_news_sm")


def tokenize(text: str) -> list[dict[str, str | bool]]:
    result = []
    doc = nlp(text)
    for token in doc:
        result.append(
            {
                "i": token.i,
                "lemma": token.lemma_.lower(),
                "pos": token.pos_,
                "morph": token.morph.to_dict(),
                "head": token.head.i,
                "text": token.text,
                "clickable": not (token.is_punct or token.is_space),
                "ws": token.whitespace_,
            }
        )
    return result


def mark_word(text: str, i: int) -> str:
    doc = nlp(text)
    if not 0 <= i < len(doc):
        raise ValueError(f"Token index {i} out of range")
    token = doc[i]
    if token.is_punct or token.is_space:
        raise ValueError(f"Token {i} ({token.text!r}) is not a word")
    start = token.idx
    end = start + len(token.text)
    return f"{text[:start]}[{token.text}]{text[end:]}"


CHECKED_FIELDS = ("case", "gender", "number")


def spacy_facts(text: str, i: int) -> dict[str, str | None]:
    morph = nlp(text)[i].morph
    facts = {}
    for field in CHECKED_FIELDS:
        values = morph.get(field.capitalize())
        # A token spaCy can't pin down gets "Masc,Neut"; it never equals the
        # model's single value, so it shows up as a mismatch to review.
        facts[field] = ",".join(values) if values else None
    return facts
