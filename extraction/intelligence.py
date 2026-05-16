from extraction.maritime_dictionary import MARITIME_TERMS


def expand_maritime_terms(text):

    words = text.split()

    expanded_words = []

    for word in words:

        clean_word = word.strip(",.:;")

        if clean_word in MARITIME_TERMS:

            expanded_words.append({
                "short_form": clean_word,
                "full_form": MARITIME_TERMS[clean_word]
            })

    return expanded_words