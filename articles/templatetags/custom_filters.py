from django import template


register = template.Library()
CENSURED_WORDS = {'content', 'pancetta', 'ground', 'ribs', 'pastrami', 'beef'} # не допускаются символы и слова меньше 2 букв
forbidden_words = CENSURED_WORDS

class InCorrectInputCensorship(Exception):
    pass


@register.filter()
def censorship(text):
    if not isinstance(text, str):
        raise InCorrectInputCensorship
    for word in CENSURED_WORDS:
        if word in text.lower():
            text = text.replace(word, word[0]+(len(word)-1)*'*')
            text = text.replace(word.capitalize(), word[0].upper()+(len(word)-1)*'*')
    return text

@register.filter()
def task34_2_6(text):
    text = text.split(" ")
    counter = 0
    for word in text:
        if word.lower() in forbidden_words:
            text[counter] = word[0] + "*"*len(word)-2 + word[-1]
        counter += 1
    return " ".join(text)