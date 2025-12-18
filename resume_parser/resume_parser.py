from collections import Counter, defaultdict
from nltk.corpus import stopwords
from pdf_parser import pdf_parser
import string


class ResumeParser:
    """
    Load, analyze, and visualize multiple text documents.
    """

    @staticmethod
    def load_stop_words(stopfile):
        """
        Load default stopwords
        """
        sw = set(stopwords.words('english'))
        if stopfile:
            with open(stopfile, 'r') as f:
                sw.update(line.strip().lower() for line in f)
        return sw

    def __init__(self, stopfile=None):
        """
        Initialize storage and stopword list
        """
        self.data = defaultdict(dict)
        self.stopwords = self.load_stop_words(stopfile)

    @staticmethod
    def default_parser(filename, stopwords=None):
        """
        parser for .txt files: lowercase, remove punctuation, split, filter, count.
        """
        with open(filename, 'r') as file:
            text = file.read().lower()

        text = text.translate(str.maketrans('', '', string.punctuation))
        words = text.split()

        if stopwords:
            words = [
                w for w in words
                if w not in stopwords
                and len(w) > 2
                and not any(ch.isdigit() for ch in w)
            ]

        return {
            "wordcount": Counter(words),
            "numwords": len(words)
        }

    def load_text(self, filename, label=None, parser=None):
        """
        Load a file, parse it, and store wordcount + metadata.
        """
        if parser is None:
            results = self.default_parser(filename, self.stopwords)
        else:
            results = parser(filename, self.stopwords)

        if label is None:
            label = filename

        for key, value in results.items():
            self.data[key][label] = value

if __name__ == "__main__":
    rp = ResumeParser()
    rp.load_text('Bridget_Crampton_Resume.pdf', parser=pdf_parser)

    print(rp.data)