import os
import re
from collections import defaultdict
from transformers import AutoTokenizer

class BPE():
    """Byte-Pair Encoding: Subword-based tokenization algorithm."""

    def __init__(self, corpus, vocab_size):
        """Initialize BPE tokenizer."""
        self.corpus = corpus
        self.vocab_size = vocab_size
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        self.word_freqs = defaultdict(int)
        self.splits = {}
        self.merges = {}

    def train(self):
        """Train BPE tokenizer."""
        # Count word frequencies
        for text in self.corpus:
            words_with_offsets = self.tokenizer.backend_tokenizer.pre_tokenizer.pre_tokenize_str(text)
            new_words = [word for word, offset in words_with_offsets]
            for word in new_words:
                self.word_freqs[word] += 1

        # Create the base vocabulary from the corpus
        alphabet = sorted(set(char for word in self.word_freqs for char in word))
        vocab = ["</w>"] + alphabet.copy()

        # Split each word into individual characters before training
        self.splits = {word: [c for c in word] for word in self.word_freqs.keys()}

        # Merge the most frequent pairs until the vocabulary size is reached
        while len(vocab) < self.vocab_size:
            pair_freqs = self.compute_pair_freqs()
            if not pair_freqs:
                break
            best_pair = max(pair_freqs, key=pair_freqs.get)
            self.splits = self.merge_pair(*best_pair)
            self.merges[best_pair] = best_pair[0] + best_pair[1]
            vocab.append(best_pair[0] + best_pair[1])
        return self.merges

    def compute_pair_freqs(self):
        """Compute the frequency of each pair."""
        pair_freqs = defaultdict(int)
        for word, freq in self.word_freqs.items():
            split = self.splits[word]
            if len(split) == 1:
                continue
            for i in range(len(split) - 1):
                pair = (split[i], split[i + 1])
                pair_freqs[pair] += freq
        return pair_freqs

    def merge_pair(self, a, b):
        """Merge the given pair."""
        new_splits = {}
        for word in self.word_freqs:
            split = self.splits[word]
            if len(split) == 1:
                new_splits[word] = split
                continue
            
            i = 0
            new_split = []
            while i < len(split):
                if i < len(split) - 1 and split[i] == a and split[i + 1] == b:
                    new_split.append(a + b)
                    i += 2
                else:
                    new_split.append(split[i])
                    i += 1
            new_splits[word] = new_split
        return new_splits

    def tokenize(self, text):
        """Tokenize a given text with trained BPE tokenizer."""
        pre_tokenize_result = self.tokenizer.backend_tokenizer.pre_tokenizer.pre_tokenize_str(text)
        pre_tokenized_text = [word for word, offset in pre_tokenize_result]
        splits_text = [[l for l in word] for word in pre_tokenized_text]

        for pair, merge in self.merges.items():
            for idx, split in enumerate(splits_text):
                i = 0
                while i < len(split) - 1:
                    if split[i] == pair[0] and split[i + 1] == pair[1]:
                        split = split[:i] + [merge] + split[i + 2:]
                    else:
                        i += 1
                splits_text[idx] = split
        result = sum(splits_text, [])
        return result

def load_tsv(file_path: str):
    """Load the TSV file and return its contents."""
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return [line.strip().split('\t') for line in lines]

def extract_index(filename: str) -> int:
    """Extract the index from the input filename."""
    match = re.search(r'data-(\d+)', filename)
    if match:
        return int(match.group(1))
    return None

def save_tokenized_data(output_dir: str, index: int, tokenized_hin: list, tokenized_tel: list):
    """Save tokenized data to the output folder with the specified naming convention."""
    output_filename = f"data-{index}_tokenized_{index}.tsv"
    output_path = os.path.join(output_dir, output_filename)
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as file:
        for hin, tel in zip(tokenized_hin, tokenized_tel):
            file.write(f"{hin}\t{tel}\n")
    return output_filename

def process_tsv_files(data_dir: str, output_dir: str, vocab_size: int):
    """Process all TSV files in the data directory with BPE and save the results."""
    hindi_sentences = []
    telugu_sentences = []
    file_data = {}

    # First, collect all sentences for training
    print("Collecting sentences for training...")
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.tsv'):
                index = extract_index(file)
                if index is not None:
                    file_path = os.path.join(root, file)
                    lines = load_tsv(file_path)
                    file_data[index] = lines
                    for hindi, telugu in lines:
                        hindi_sentences.append(hindi)
                        telugu_sentences.append(telugu)

    # Train tokenizers
    print(f"Training tokenizers with vocab size {vocab_size}...")
    hindi_tokenizer = BPE(hindi_sentences, vocab_size)
    telugu_tokenizer = BPE(telugu_sentences, vocab_size)

    print("Training Hindi tokenizer...")
    hindi_tokenizer.train()
    print("Training Telugu tokenizer...")
    telugu_tokenizer.train()

    # Process each file
    processed_files = []
    for index, lines in sorted(file_data.items()):
        print(f"Processing file with index: {index}")
        tokenized_hindi = []
        tokenized_telugu = []
        
        for hindi, telugu in lines:
            tokenized_hindi.append(" ".join(hindi_tokenizer.tokenize(hindi)))
            tokenized_telugu.append(" ".join(telugu_tokenizer.tokenize(telugu)))

        tokenized_filename = save_tokenized_data(output_dir, index, tokenized_hindi, tokenized_telugu)
        processed_files.append(tokenized_filename)
        print(f"Saved tokenized file: {tokenized_filename}")

    print(f"Total files processed: {len(processed_files)}")
    return processed_files

if __name__ == "__main__":
    data_dir = 'data_aligned'
    output_dir = 'data_tokenized'
    vocab_size = 1000

    processed_files = process_tsv_files(data_dir, output_dir, vocab_size)
    
    # Verify the number of files
    input_files = [f for f in os.listdir(data_dir) if f.endswith('.tsv')]
    print(f"Number of input files: {len(input_files)}")
    print(f"Number of output files: {len(processed_files)}")

    if len(input_files) != len(processed_files):
        print("Warning: Number of input and output files don't match!")
        print("Input files:", sorted(input_files))
        print("Output files:", sorted(processed_files))
        
        # Check which indices are missing
        input_indices = set(extract_index(f) for f in input_files if extract_index(f) is not None)
        output_indices = set(extract_index(f) for f in processed_files if extract_index(f) is not None)
        missing_indices = input_indices - output_indices
        if missing_indices:
            print("Missing indices:", sorted(missing_indices))