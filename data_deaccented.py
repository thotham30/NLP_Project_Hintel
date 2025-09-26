import os
import re
import unicodedata

def deaccent_text(text):
    # Convert accented characters to their base form
    nfkd_form = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def process_srt_file_deaccent(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
        subtitle_text = []
        for line in infile:
            line = line.strip()
            if re.match(r'^\d+$', line) or '-->' in line:
                # Subtitle number or timestamp - write as is
                if subtitle_text:
                    deaccented_text = deaccent_text(' '.join(subtitle_text))
                    outfile.write(deaccented_text + '\n\n')
                    subtitle_text = []
                outfile.write(line + '\n')
            elif line:
                # Subtitle text - collect for deaccenting
                subtitle_text.append(line)
            else:
                # Empty line - write as is
                if subtitle_text:
                    deaccented_text = deaccent_text(' '.join(subtitle_text))
                    outfile.write(deaccented_text + '\n\n')
                    subtitle_text = []
                else:
                    outfile.write('\n')
        
        # Handle any remaining subtitle text
        if subtitle_text:
            deaccented_text = deaccent_text(' '.join(subtitle_text))
            outfile.write(deaccented_text + '\n')

# Directory paths
source_directory = "data_invalid_lang_range_cleaned"
destination_directory = 'data_deaccented'

os.makedirs(destination_directory, exist_ok=True)

for root, dirs, files in os.walk(source_directory):
    for file in files:
        if file.endswith(".srt"):
            source_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(root, source_directory)
            dest_folder = os.path.join(destination_directory, relative_path)
            os.makedirs(dest_folder, exist_ok=True)
            output_file_path = os.path.join(dest_folder, file)
            
            process_srt_file_deaccent(source_file_path, output_file_path)
            print(f"Processed: {source_file_path} -> {output_file_path}")

print("All files have been processed and saved to 'data-deaccented'.")