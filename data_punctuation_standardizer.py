import os
import re
import unicodedata

def expanded_standardize_punctuation(text):
    # Expanded punctuation mapping
    punct_map = {
        # Basic punctuation
        '।': '.', # Hindi full stop to period
        '॥': '.', # Hindi double danda to period
        'ред': '.', # Telugu full stop to period
        '…': '...', # Ellipsis
        '‥': '..', # Two-dot leader to double period
        
        # Quotes
        ''': "'", ''': "'", # Single quotes
        '"': '"', '"': '"', # Double quotes
        '„': '"', '‟': '"', # Double low-9 quotation mark and reversed double quotation mark
        '「': '"', '」': '"', # Corner brackets as quotes
        '『': ''', '』': ''', # White corner brackets as single quotes
        
        # Dashes and Hyphens
        '—': '-', '–': '-', # Em dash and en dash to hyphen
        '‐': '-', '‑': '-', '‒': '-', # Various Unicode hyphens to ASCII hyphen
        
        # Other punctuation
        '،': ',', # Arabic comma to comma
        '、': ',', # Ideographic comma to comma
        '；': ';', # Fullwidth semicolon to semicolon
        '：': ':', # Fullwidth colon to colon
        '！': '!', # Fullwidth exclamation mark to ASCII
        '？': '?', # Fullwidth question mark to ASCII
        '（': '(', '）': ')', # Fullwidth parentheses to ASCII
        '［': '[', '］': ']', # Fullwidth square brackets to ASCII
        '｛': '{', '｝': '}', # Fullwidth curly braces to ASCII
        '《': '<', '》': '>', # Double angle brackets to less/greater than
        '〈': '<', '〉': '>', # Single angle brackets to less/greater than
        
        # Hindi-specific
        '॰': '.', # Abbreviation sign to period
        
        # Telugu-specific
        'ఽ': "'", # Telugu sign avagraha to apostrophe
    }
    
    def replace_punct(match):
        char = match.group(0)
        return punct_map.get(char, char)
    
    # Replace punctuation using the mapping
    text = re.sub(r'[^\w\s]', replace_punct, text)
    
    # Normalize Unicode characters
    text = unicodedata.normalize('NFKC', text)
    
    # Standardize spaces around punctuation
    text = re.sub(r'\s+([.,:;!?])', r'\1', text)  # Remove space before
    text = re.sub(r'([.,:;!?])(?=\S)', r'\1 ', text)  # Add space after if followed by non-space
    
    # Standardize multiple punctuation
    text = re.sub(r'\.{2,}', '...', text)  # Replace multiple dots with ellipsis
    text = re.sub(r'!{2,}', '!', text)  # Replace multiple exclamation marks with single
    text = re.sub(r'\?{2,}', '?', text)  # Replace multiple question marks with single
    
    # Standardize space after sentence-ending punctuation
    text = re.sub(r'([.!?])(\s*)([^"\'])', r'\1 \3', text)
    
    # Remove spaces at the beginning and end of lines
    text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)
    
    # Ensure single space between words
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def process_srt_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
        subtitle_text = []
        for line in infile:
            line = line.strip()
            if re.match(r'^\d+$', line) or '-->' in line:
                # Subtitle number or timestamp - write as is
                if subtitle_text:
                    standardized_text = expanded_standardize_punctuation(' '.join(subtitle_text))
                    outfile.write(standardized_text + '\n\n')
                    subtitle_text = []
                outfile.write(line + '\n')
            elif line:
                # Subtitle text - collect for standardization
                subtitle_text.append(line)
            else:
                # Empty line - write as is
                if subtitle_text:
                    standardized_text = expanded_standardize_punctuation(' '.join(subtitle_text))
                    outfile.write(standardized_text + '\n\n')
                    subtitle_text = []
                else:
                    outfile.write('\n')
        
        # Handle any remaining subtitle text
        if subtitle_text:
            standardized_text = expanded_standardize_punctuation(' '.join(subtitle_text))
            outfile.write(standardized_text + '\n')

# Directory paths
source_directory = r"./data_bg_cleaned"
destination_directory = r"./data_punctuation_standardized"

os.makedirs(destination_directory, exist_ok=True)

for root, dirs, files in os.walk(source_directory):
    for file in files:
        if file.endswith(".srt"):
            source_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(root, source_directory)
            dest_folder = os.path.join(destination_directory, relative_path)
            os.makedirs(dest_folder, exist_ok=True)
            output_file_path = os.path.join(dest_folder, file)
            
            process_srt_file(source_file_path, output_file_path)
            print(f"Processed: {source_file_path} -> {output_file_path}")

print("All files have been processed and saved to 'data_punctuation_standardized'.")