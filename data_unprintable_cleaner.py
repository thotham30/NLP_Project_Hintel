import os
import unicodedata

def remove_non_printable(text):
    return ''.join(c for c in text if not unicodedata.category(c).startswith('C'))

source_directory = "data_Html_cleaned"  # Replace with the path to the 'data-encoded' folder
destination_directory = "data_unprintable_cleaned"  # Replace with the path to the 'data-unprintable-cleaned' folder

os.makedirs(destination_directory, exist_ok=True)

for root, dirs, files in os.walk(source_directory):
    for file in files:
        if file.endswith(".srt"):
            source_file_path = os.path.join(root, file)
            print(f"Processing file: {source_file_path}")
            
            relative_path = os.path.relpath(root, source_directory)
            dest_folder = os.path.join(destination_directory, relative_path)
            os.makedirs(dest_folder, exist_ok=True)

            output_file_path = os.path.join(dest_folder, file)
            
            with open(source_file_path, 'r', encoding='utf-8') as srt_file:
                lines = srt_file.readlines()

            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                for line in lines:
                    if '-->' not in line and line.strip():
                        cleaned_line = remove_non_printable(line)
                        output_file.write(cleaned_line + '\n')
                    else:
                        output_file.write(line)

            print(f"unprintable char Cleaned file saved at: {output_file_path}")

print("All files have been processed and saved to 'data-unprintable-cleaned'.")