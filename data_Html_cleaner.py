import os
import re

source_base_dir = 'data_lang_cleaned'  # Replace with the actual path to your data folder
destination_base_dir = 'data_Html_cleaned'  # Replace with the actual path to your data-bg-cleaned folder

rtl_embed = '\u202B'
pop_directional_formatting = '\u202C'

os.makedirs(destination_base_dir, exist_ok=True)

def clean_text(text):
    text = text.replace(rtl_embed, '')
    text = text.replace(pop_directional_formatting, '')
    
    text = re.sub(r'<i>|</i>', '', text)
    
    return text

for folder in os.listdir(source_base_dir):
    folder_path = os.path.join(source_base_dir, folder)

    if os.path.isdir(folder_path) and folder.startswith('data-'):
        destination_folder = os.path.join(destination_base_dir, folder)
        os.makedirs(destination_folder, exist_ok=True)

        for file_name in os.listdir(folder_path):
            if file_name.startswith('hin-') or file_name.startswith('tel-'):
                source_file_path = os.path.join(folder_path, file_name)
                destination_file_path = os.path.join(destination_folder, file_name)

                with open(source_file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                cleaned_content = clean_text(content)

                with open(destination_file_path, 'w', encoding='utf-8') as cleaned_file:
                    cleaned_file.write(cleaned_content)
                
                print(f"Cleaned {file_name} in folder {folder}")