import spacy


nlp = spacy.load("de_core_news_sm")


def tokenize(text: str) -> list[dict[str, str | bool]]:
    result = []
    doc = nlp(text)
    for token in doc:
        result.append(
            {
                "lemma": token.lemma_.lower(),
                "text": token.text,
                "clickable": not (token.is_punct or token.is_space),
                "ws": token.whitespace_,
            }
        )
    return result
