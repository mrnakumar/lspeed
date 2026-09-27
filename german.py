import spacy


nlp = spacy.load("de_core_news_sm")


def find_new_words(text: str | None, known: set[str], free_words: set[str]) -> set[str]:
    if not text:
        raise ValueError("Text is empty or None")
    new_words = set()
    doc = nlp(text)
    for token in doc:
        if not token.is_punct and not token.is_space:
            lemma = token.lemma_.lower()
            if lemma not in known and lemma not in free_words:
                pos = token.pos_
                if pos in ["NOUN", "VERB", "ADJ", "ADV"]:
                    new_words.add(lemma)
    return new_words


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


def load_words(path: str) -> set[str]:
    with open(path, "r") as f:
        return {
            stripped.lower()
            for line in f.readlines()
            if ((stripped := line.strip()) and not stripped.startswith("#"))
        }

    # {word.lower() for word in german.load_words(FILE_FREE_WORDS)}
