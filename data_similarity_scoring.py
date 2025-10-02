import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from collections import defaultdict
import re
from typing import List, Tuple, Set, Dict
import unicodedata

class AdvancedSimilarityCalculator:
    def __init__(self):
        self.char_vectorizer = TfidfVectorizer(
            lowercase=False, 
            analyzer='char',
            ngram_range=(1, 3)
        )
        self.structure_vectorizer = TfidfVectorizer(
            lowercase=False,
            analyzer='char',
            ngram_range=(2, 5),
            token_pattern=None
        )
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text by removing extra spaces and diacritics."""
        text = ' '.join(text.split())
        return ''.join(c for c in unicodedata.normalize('NFKD', text)
                      if not unicodedata.combining(c))
    
    def _get_text_structure(self, text: str) -> str:
        """Extract structural features from text."""
        # Replace characters with their Unicode category
        structure = [unicodedata.category(c) for c in text]
        # Keep spaces and punctuation
        for i, c in enumerate(text):
            if c.isspace() or unicodedata.category(c).startswith('P'):
                structure[i] = c
        return ''.join(structure)
    
    def _get_ngrams(self, text: str, n_range: Tuple[int, int] = (1, 3)) -> Set[str]:
        """Generate character n-grams from text."""
        ngrams = set()
        normalized_text = self._normalize_text(text)
        for n in range(n_range[0], n_range[1] + 1):
            for i in range(len(normalized_text) - n + 1):
                ngrams.add(normalized_text[i:i+n])
        return ngrams

    def calculate_similarity_score(self, text1: str, text2: str) -> float:
        """Calculate a combined similarity score."""
        # Calculate different types of similarities
        char_similarity = self._calculate_char_similarity(text1, text2)
        struct_similarity = self._calculate_structural_similarity(text1, text2)
        length_similarity = self._calculate_length_similarity(text1, text2)
        
        # Weighted combination of similarities
        weights = [0.5, 0.3, 0.2]  # Adjust these weights as needed
        combined_score = (
            weights[0] * char_similarity +
            weights[1] * struct_similarity +
            weights[2] * length_similarity
        )
        return combined_score

    def _calculate_char_similarity(self, text1: str, text2: str) -> float:
        """Calculate character-level similarity."""
        try:
            vectors = self.char_vectorizer.fit_transform([text1, text2])
            return cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        except ValueError:
            return 0.0

    def _calculate_structural_similarity(self, text1: str, text2: str) -> float:
        """Calculate structural similarity."""
        struct1 = self._get_text_structure(text1)
        struct2 = self._get_text_structure(text2)
        try:
            vectors = self.structure_vectorizer.fit_transform([struct1, struct2])
            return cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        except ValueError:
            return 0.0

    def _calculate_length_similarity(self, text1: str, text2: str) -> float:
        """Calculate length-based similarity."""
        len1, len2 = len(text1), len(text2)
        return 1 - abs(len1 - len2) / max(len1, len2)

class ParallelTextProcessor:
    def __init__(self, calculator: AdvancedSimilarityCalculator):
        self.calculator = calculator
    
    def load_tokenized_data(self, file_path: str) -> Tuple[List[str], List[str]]:
        hindi_texts, telugu_texts = [], []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    hindi, telugu = line.strip().split('\t')
                    hindi_texts.append(hindi)
                    telugu_texts.append(telugu)
                except ValueError:
                    print(f"Skipping malformed line: {line.strip()}")
        return hindi_texts, telugu_texts
    
    def process_file(self, input_path: str, output_path: str) -> None:
        hindi_texts, telugu_texts = self.load_tokenized_data(input_path)
        
        if not hindi_texts or not telugu_texts:
            print(f"Skipping empty file: {input_path}")
            return
        
        similarities = [
            self.calculator.calculate_similarity_score(h, t)
            for h, t in zip(hindi_texts, telugu_texts)
        ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("Hindi\tTelugu\tSimilarity_Score\n")
            for h, t, s in zip(hindi_texts, telugu_texts, similarities):
                f.write(f"{h}\t{t}\t{s:.4f}\n")

def process_directory(input_dir: str, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    calculator = AdvancedSimilarityCalculator()
    processor = ParallelTextProcessor(calculator)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.tsv'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f'similarity_{filename}')
            processor.process_file(input_path, output_path)
            print(f"Processed {filename}")

def run_tests() -> None:
    calculator = AdvancedSimilarityCalculator()
    
    test_cases = [
        # Similar meaning, different scripts
        ("मैं घर जा रहा हूं", "నేను ఇంటికి వెళ్తున్నాను"),
        # Different meaning, similar structure
        ("क्या आप ठीक हैं?", "మీరు బాగున్నారా?"),
        # Very different
        ("नमस्ते दुनिया", "హలో ప్రపంచం"),
        # Similar length and structure
        ("मैं स्कूल जाता हूं", "నేను స్కూలుకి వెళ్తాను"),
    ]
    
    print("Running tests...")
    for i, (hindi, telugu) in enumerate(test_cases, 1):
        print(f"\nTest case {i}:")
        print(f"Hindi: {hindi}")
        print(f"Telugu: {telugu}")
        
        similarity = calculator.calculate_similarity_score(hindi, telugu)
        print(f"Similarity score: {similarity:.4f}")

if __name__ == "__main__":
    run_tests()
    
    print("\nProcessing actual files...")
    input_dir = 'data_tokenized'
    output_dir = 'data_similarity_scoring'
    process_directory(input_dir, output_dir)