import os
import re

def remove_non_hindi_telugu(text):
    cleaned_text = re.sub(r'[^\u0900-\u097F\u0C00-\u0C7F\u0964\u0965\u0020-\u007F]', '', text)
    return cleaned_text.strip()

source_directory = "data_unprintable_cleaned"  
destination_directory = "data_invalid_lang_range_cleaned" 


os.makedirs(destination_directory, exist_ok=True)

changes_made = False

for root, dirs, files in os.walk(source_directory):
    for file in files:
        if file.endswith(".srt"):
            source_file_path = os.path.join(root, file)
            print(f"\nProcessing file: {source_file_path}")
            
            relative_path = os.path.relpath(root, source_directory)
            dest_folder = os.path.join(destination_directory, relative_path)
            os.makedirs(dest_folder, exist_ok=True)

            output_file_path = os.path.join(dest_folder, file)
            
            with open(source_file_path, 'r', encoding='utf-8') as srt_file:
                lines = srt_file.readlines()

            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                for line in lines:
                    if '-->' not in line and line.strip():
                        cleaned_line = remove_non_hindi_telugu(line)
                        
                        if line.strip() != cleaned_line:
                            changes_made = True
                            print(f"Changed line:\nOriginal: {line.strip()}\nCleaned: {cleaned_line}\n")

                        output_file.write(cleaned_line + '\n')
                    else:
                        output_file.write(line)

            if not changes_made:
                print(f"No changes made in {source_file_path}.")
            else:
                print(f"Cleaned file saved at: {output_file_path}")

            changes_made = False

print("All files have been processed and saved to 'data-lang-cleaned'.")
