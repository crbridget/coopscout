import math
from resume_parser import ResumeParser


class JobResumeMatchScorer:
    """
    Calculate similarity and match scores between resumes and job descriptions.
    Provides multiple scoring metrics to evaluate how well a resume matches a job.
    """

    def __init__(self, resume_parser):
        """
        Initialize with a ResumeParser instance that has loaded documents.

        Args:
            resume_parser: Instance of ResumeParser with loaded documents
        """
        self.parser = resume_parser

    def compute_cosine_similarity(self, label1, label2):
        """
        Calculate cosine similarity between two documents based on word counts.
        This measures the angle between two word-frequency vectors.

        Returns:
            Float between 0 and 1, where 1 is identical and 0 is completely different.
        """
        if label1 not in self.parser.data['wordcount'] or label2 not in self.parser.data['wordcount']:
            raise ValueError(f"Labels '{label1}' or '{label2}' not found in loaded documents")

        counter1 = self.parser.data['wordcount'][label1]
        counter2 = self.parser.data['wordcount'][label2]

        # Get all unique words from both documents
        all_words = set(counter1.keys()) | set(counter2.keys())

        # Calculate dot product
        dot_product = sum(counter1.get(word, 0) * counter2.get(word, 0) for word in all_words)

        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(count ** 2 for count in counter1.values()))
        magnitude2 = math.sqrt(sum(count ** 2 for count in counter2.values()))

        # Avoid division by zero
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def compute_jaccard_similarity(self, label1, label2):
        """
        Calculate Jaccard similarity between two documents (unique words overlap).
        This measures the ratio of shared words to total unique words.

        Returns:
            Float between 0 and 1.
        """
        if label1 not in self.parser.data['wordcount'] or label2 not in self.parser.data['wordcount']:
            raise ValueError(f"Labels '{label1}' or '{label2}' not found in loaded documents")

        words1 = set(self.parser.data['wordcount'][label1].keys())
        words2 = set(self.parser.data['wordcount'][label2].keys())

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        if union == 0:
            return 0.0

        return intersection / union

    def compute_keyword_coverage(self, resume_label, job_label, top_n=50):
        """
        Calculate what percentage of the top N keywords in the job description
        appear in the resume. This is directional - it shows how well the resume
        covers important job requirements.

        Args:
            resume_label: Label for the resume document
            job_label: Label for the job description document
            top_n: Number of top keywords to consider from job description

        Returns:
            Float between 0 and 1 representing coverage percentage.
        """
        if resume_label not in self.parser.data['wordcount'] or job_label not in self.parser.data['wordcount']:
            raise ValueError(f"Labels not found in loaded documents")

        job_counter = self.parser.data['wordcount'][job_label]
        resume_words = set(self.parser.data['wordcount'][resume_label].keys())

        # Get top N keywords from job description
        top_job_keywords = set(word for word, _ in job_counter.most_common(top_n))

        # Calculate coverage
        matched_keywords = top_job_keywords & resume_words

        if len(top_job_keywords) == 0:
            return 0.0

        return len(matched_keywords) / len(top_job_keywords)

    def calculate_match_score(self, resume_label, job_label, weights=None):
        """
        Calculate a comprehensive match score between resume and job description.
        Combines multiple metrics into a single score.

        Args:
            resume_label: Label for the resume document
            job_label: Label for the job description document
            weights: Dict with keys 'cosine', 'jaccard', 'coverage'
                    (default: {'cosine': 0.4, 'jaccard': 0.3, 'coverage': 0.3})

        Returns:
            Dict containing:
                - Individual similarity scores (0-1 scale)
                - Total weighted score (0-100 scale)
                - Match level categorization
        """
        if weights is None:
            weights = {'cosine': 0.4, 'jaccard': 0.3, 'coverage': 0.3}

        # Validate weights sum to 1.0
        weight_sum = sum(weights.values())
        if not math.isclose(weight_sum, 1.0, rel_tol=1e-5):
            raise ValueError(f"Weights must sum to 1.0, got {weight_sum}")

        cosine_score = self.compute_cosine_similarity(resume_label, job_label)
        jaccard_score = self.compute_jaccard_similarity(resume_label, job_label)
        coverage_score = self.compute_keyword_coverage(resume_label, job_label)

        # Calculate weighted total (0-100 scale)
        total_score = (
                              cosine_score * weights['cosine'] +
                              jaccard_score * weights['jaccard'] +
                              coverage_score * weights['coverage']
                      ) * 100

        return {
            'cosine_similarity': round(cosine_score, 4),
            'jaccard_similarity': round(jaccard_score, 4),
            'keyword_coverage': round(coverage_score, 4),
            'total_score': round(total_score, 2),
            'match_level': self._get_match_level(total_score)
        }

    @staticmethod
    def _get_match_level(score):
        """
        Categorize match score into human-readable levels.

        Args:
            score: Match score (0-100)

        Returns:
            String describing match quality
        """
        if score >= 75:
            return 'Excellent Match'
        elif score >= 60:
            return 'Good Match'
        elif score >= 45:
            return 'Fair Match'
        elif score >= 30:
            return 'Weak Match'
        else:
            return 'Poor Match'

    def get_missing_keywords(self, resume_label, job_label, top_n=20):
        """
        Identify important keywords from the job description that are missing
        from the resume. This helps identify gaps in the resume.

        Args:
            resume_label: Label for the resume document
            job_label: Label for the job description document
            top_n: Number of missing keywords to return

        Returns:
            List of (word, count) tuples showing missing keywords and their
            frequency in the job description
        """
        if resume_label not in self.parser.data['wordcount'] or job_label not in self.parser.data['wordcount']:
            raise ValueError(f"Labels not found in loaded documents")

        job_counter = self.parser.data['wordcount'][job_label]
        resume_words = set(self.parser.data['wordcount'][resume_label].keys())

        # Find top job keywords not in resume
        missing = [
            (word, count) for word, count in job_counter.most_common(100)
            if word not in resume_words
        ]

        return missing[:top_n]

    def get_shared_keywords(self, resume_label, job_label, top_n=20):
        """
        Identify keywords that appear in both the resume and job description.
        These are the strengths of the match.

        Args:
            resume_label: Label for the resume document
            job_label: Label for the job description document
            top_n: Number of shared keywords to return

        Returns:
            List of (word, job_count, resume_count) tuples
        """
        if resume_label not in self.parser.data['wordcount'] or job_label not in self.parser.data['wordcount']:
            raise ValueError(f"Labels not found in loaded documents")

        job_counter = self.parser.data['wordcount'][job_label]
        resume_counter = self.parser.data['wordcount'][resume_label]

        # Find words in both documents
        shared_words = set(job_counter.keys()) & set(resume_counter.keys())

        # Sort by job description frequency
        shared = [
            (word, job_counter[word], resume_counter[word])
            for word in shared_words
        ]
        shared.sort(key=lambda x: x[1], reverse=True)

        return shared[:top_n]


if __name__ == "__main__":
    # Example usage
    from pdf_parser import pdf_parser

    # Initialize parser and load documents
    rp = ResumeParser()
    rp.load_text('Bridget_Crampton_Resume.pdf', label='resume', parser=pdf_parser)

    # Example job description
    job_text = """
    Software Engineer - Full Stack Development

    We are seeking a talented Software Engineer to join our team. The ideal candidate
    will have strong experience with Python, JavaScript, and React. You will be responsible
    for developing web applications, building APIs, and working with databases like PostgreSQL.

    Requirements:
    - Bachelor's degree in Computer Science or related field
    - 2+ years of experience in software development
    - Proficiency in Python and modern web frameworks (Flask, Django)
    - Experience with frontend technologies (React, JavaScript, HTML, CSS)
    - Strong understanding of database design and SQL
    - Experience with version control (Git)
    - Excellent problem-solving and communication skills

    Nice to have:
    - Experience with web scraping and automation
    - Knowledge of machine learning or data science
    - Familiarity with cloud platforms (AWS, Azure)
    - Experience with Agile development methodologies
    """

    rp.load_text_from_string(job_text, label='job')

    # Create scorer and calculate match
    scorer = JobResumeMatchScorer(rp)

    print("=" * 60)
    print("RESUME-JOB MATCH ANALYSIS")
    print("=" * 60)

    # Calculate overall match score
    match_results = scorer.calculate_match_score('resume', 'job')
    print(f"\nOVERALL MATCH SCORE: {match_results['total_score']}%")
    print(f"Match Level: {match_results['match_level']}")
    print(f"\nDetailed Scores:")
    print(f"  Cosine Similarity: {match_results['cosine_similarity']:.4f}")
    print(f"  Jaccard Similarity: {match_results['jaccard_similarity']:.4f}")
    print(f"  Keyword Coverage: {match_results['keyword_coverage']:.4f}")

    # Show shared keywords (strengths)
    print(f"\n{'=' * 60}")
    print("SHARED KEYWORDS (Strengths)")
    print("=" * 60)
    shared = scorer.get_shared_keywords('resume', 'job', top_n=15)
    print(f"{'Keyword':<20} {'Job Count':<12} {'Resume Count'}")
    print("-" * 60)
    for word, job_count, resume_count in shared:
        print(f"{word:<20} {job_count:<12} {resume_count}")

    # Show missing keywords (gaps)
    print(f"\n{'=' * 60}")
    print("MISSING KEYWORDS (Potential Gaps)")
    print("=" * 60)
    missing = scorer.get_missing_keywords('resume', 'job', top_n=15)
    print(f"{'Keyword':<30} {'Frequency in Job'}")
    print("-" * 60)
    for word, count in missing:
        print(f"{word:<30} {count}")

    print("\n" + "=" * 60)