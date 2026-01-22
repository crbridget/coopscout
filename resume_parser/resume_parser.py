from collections import Counter, defaultdict
from nltk.corpus import stopwords
from pdf_parser import pdf_parser
import string


class ResumeParser:
    """
    Load, analyze, and parse multiple text documents (resumes, job descriptions, etc.)
    """

    @staticmethod
    def load_stop_words(stopfile):
        """
        Load default stopwords from NLTK and optionally from a custom file
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
        Parser for .txt files: lowercase, remove punctuation, split, filter, count.
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

        Args:
            filename: Path to the file to load
            label: Custom label for this document (defaults to filename)
            parser: Custom parser function (defaults to default_parser)
        """
        if parser is None:
            results = self.default_parser(filename, self.stopwords)
        else:
            results = parser(filename, self.stopwords)

        if label is None:
            label = filename

        for key, value in results.items():
            self.data[key][label] = value

    def load_text_from_string(self, text, label):
        """
        Load text directly from a string instead of a file.
        Useful for loading job descriptions from database.

        Args:
            text: The text content to parse
            label: Label for this document
        """
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        words = text.split()

        words = [
            w for w in words
            if w not in self.stopwords
               and len(w) > 2
               and not any(ch.isdigit() for ch in w)
        ]

        results = {
            "wordcount": Counter(words),
            "numwords": len(words)
        }

        for key, value in results.items():
            self.data[key][label] = value

    def get_top_words(self, label, n=10):
        """
        Get the top N most common words from a document.

        Args:
            label: Document label
            n: Number of top words to return

        Returns:
            List of (word, count) tuples
        """
        if label not in self.data['wordcount']:
            raise ValueError(f"Label '{label}' not found in loaded documents")

        return self.data['wordcount'][label].most_common(n)

    def get_document_stats(self, label):
        """
        Get statistics about a loaded document.

        Returns:
            Dict with total words, unique words, and top words
        """
        if label not in self.data['wordcount']:
            raise ValueError(f"Label '{label}' not found in loaded documents")

        return {
            'total_words': self.data['numwords'][label],
            'unique_words': len(self.data['wordcount'][label]),
            'top_10_words': self.get_top_words(label, 10)
        }


if __name__ == "__main__":
    # Example usage
    rp = ResumeParser()

    # Load resume from PDF
    rp.load_text('Bridget_Crampton_Resume.pdf', label='resume', parser=pdf_parser)

    # Example: Load job description from string
    job_text = """
    We are seeking a Software Engineer with experience in Python, JavaScript, and React.
    The ideal candidate will have strong problem-solving skills and experience with 
    databases like PostgreSQL. Experience with web scraping and API development is a plus.
    """
    rp.load_text_from_string(job_text, label='job_example')

    # Print statistics
    print("Resume Statistics:")
    stats = rp.get_document_stats('resume')
    print(f"Total words: {stats['total_words']}")
    print(f"Unique words: {stats['unique_words']}")
    print(f"\nTop 10 words:")
    for word, count in stats['top_10_words']:
        print(f"  {word}: {count}")

    print("\n" + "=" * 50 + "\n")

    print("Job Description Statistics:")
    job_stats = rp.get_document_stats('job_example')
    print(f"Total words: {job_stats['total_words']}")
    print(f"Unique words: {job_stats['unique_words']}")
    print(f"\nTop 10 words:")
    for word, count in job_stats['top_10_words']:
        print(f"  {word}: {count}")