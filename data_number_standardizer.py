import os
import re

def standardize_numbers(text):
    # Define a dictionary for Indic to Arabic numeral mapping (Hindi and Bengali numerals)
    indic_to_arabic = {
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9',
        '১': '1', '২': '2', '৩': '3', '৪': '4', 
        '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'
    }
    
    # Replace all Indic numerals with Arabic numerals using regex
    def replace_indic_numerals(match):
        return indic_to_arabic.get(match.group(0), match.group(0))
    
    # Replace any Indic numeral found in the text
    return re.sub(r'[०-९১-৯]', replace_indic_numerals, text)

def process_srt_file_with_numbers(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
        subtitle_text = []
        for line in infile:
            line = line.strip()
            if re.match(r'^\d+$', line) or '-->' in line:
                # Subtitle number or timestamp - write as is
                if subtitle_text:
                    standardized_text = standardize_numbers(' '.join(subtitle_text))
                    outfile.write(standardized_text + '\n\n')
                    subtitle_text = []
                outfile.write(line + '\n')
            elif line:
                # Subtitle text - collect for standardization
                subtitle_text.append(line)
            else:
                # Empty line - write as is
                if subtitle_text:
                    standardized_text = standardize_numbers(' '.join(subtitle_text))
                    outfile.write(standardized_text + '\n\n')
                    subtitle_text = []
                else:
                    outfile.write('\n')
        
        # Handle any remaining subtitle text
        if subtitle_text:
            standardized_text = standardize_numbers(' '.join(subtitle_text))
            outfile.write(standardized_text + '\n')

# Directory paths
source_directory = r"./data_punctuation_standardized"
destination_directory = r"./data_number_standardized"

os.makedirs(destination_directory, exist_ok=True)

for root, dirs, files in os.walk(source_directory):
    for file in files:
        if file.endswith(".srt"):
            source_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(root, source_directory)
            dest_folder = os.path.join(destination_directory, relative_path)
            os.makedirs(dest_folder, exist_ok=True)
            output_file_path = os.path.join(dest_folder, file)
            
            process_srt_file_with_numbers(source_file_path, output_file_path)
            print(f"Processed: {source_file_path} -> {output_file_path}")

print("All files have been processed and saved to 'data-number-standardized'.")