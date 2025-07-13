from django import template


register = template.Library()
CENSURED_WORDS = {'content', 'pancetta', 'ground', 'ribs', 'pastrami', 'beef'} # не допускаются символы и слова меньше 2 букв


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