import json
import string
import re
from collections import Counter
from pypdf import PdfReader

def pdf_parser(filename, stopwords=None):
    """
        Parse PDF file and extract word counts from all pages.

        Args:
            filename (str): Path to PDF file
            stopwords (set): Optional set of words to filter out

        Returns:
            dict: {'wordcount': Counter object, 'numwords': int}
        """
    # open/read PDF file
    reader = PdfReader(filename)

    # extract text from all pages
    text = ""  # Start with empty string
    for page in reader.pages:  # Loop through each page
        text += page.extract_text()  # Add each page's text

    # clean text
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))

    words = text.split()


    # filter stopwords if provided
    if stopwords:
        words = [word for word in words
                 if word not in stopwords
                 and len(word) > 2
                 and not any(char.isdigit() for char in word)]

        # return in dict format
    return {'wordcount': Counter(words),
            'numwords': len(words)}
