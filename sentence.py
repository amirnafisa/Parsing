from nltk.tokenize import word_tokenize
class Sentence:
    def __init__ (self, sentence_string):
        self._sentence_string = sentence_string
        self._words = word_tokenize(sentence_string)

    def print_sentence(self):
        print("Sentence: ",self._sentence_string)

    def get_tokens(self):
        return self._words

    def get_unique_tokens(self):
        return set(self._words)
