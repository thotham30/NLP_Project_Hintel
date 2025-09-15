import os
import shutil
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Set seed for consistent language detection results
DetectorFactory.seed = 0

# Path to the main data folder and output folders
data_folder = "data_number_standardized"
cleaned_folder = "data_lang_cleaned"
invalid_folder = "lang_clean_invalid"

# List to hold the folders where files were modified
modified_folders = []

# Ensure output directories exist
os.makedirs(cleaned_folder, exist_ok=True)
os.makedirs(invalid_folder, exist_ok=True)

# Iterate through the index folders inside the data folder
folders = sorted(os.listdir(data_folder))

# Iterate through the index folders inside the data folder
for folder_name in folders:
    folder_path = os.path.join(data_folder, folder_name)

    # Check if it's a directory
    if os.path.isdir(folder_path):
        # Extract the folder index from the folder name (e.g., 'data-1' -> '1')
        folder_index = folder_name.split('-')[-1]

        # Construct file paths for Hindi and Telugu files
        hindi_file = os.path.join(folder_path, f"hin-{folder_index}.srt")
        telugu_file = os.path.join(folder_path, f"tel-{folder_index}.srt")

        # Paths for cleaned and invalid files
        cleaned_folder_path = os.path.join(cleaned_folder, folder_name)
        invalid_folder_path = os.path.join(invalid_folder, folder_name)

        # Ensure the cleaned folder exists
        os.makedirs(cleaned_folder_path, exist_ok=True)

        # Copy both files to the cleaned folder
        cleaned_hindi_file = os.path.join(cleaned_folder_path, f"hin-{folder_index}.srt")
        cleaned_telugu_file = os.path.join(cleaned_folder_path, f"tel-{folder_index}.srt")
        shutil.copy(hindi_file, cleaned_hindi_file)
        shutil.copy(telugu_file, cleaned_telugu_file)

        try:
            # Read and detect the language of the Hindi file
            with open(hindi_file, 'r', encoding='utf-8') as h_file:
                hindi_text = h_file.read()
                try:
                    detected_hindi_lang = detect(hindi_text)
                except LangDetectException:
                    detected_hindi_lang = None  # Handle cases with empty or undetectable content

            # Read and detect the language of the Telugu file
            with open(telugu_file, 'r', encoding='utf-8') as t_file:
                telugu_text = t_file.read()
                try:
                    detected_telugu_lang = detect(telugu_text)
                except LangDetectException:
                    detected_telugu_lang = None  # Handle cases with empty or undetectable content

            # If either the Hindi file is not detected as 'hi' or the Telugu file is not detected as 'te'
            if detected_hindi_lang != 'hi' or detected_telugu_lang != 'te':
                # Move invalid files to the invalid folder
                os.makedirs(invalid_folder_path, exist_ok=True)
                invalid_hindi_file = os.path.join(invalid_folder_path, f"hin-{folder_index}.srt")
                invalid_telugu_file = os.path.join(invalid_folder_path, f"tel-{folder_index}.srt")
                shutil.move(cleaned_hindi_file, invalid_hindi_file)
                shutil.move(cleaned_telugu_file, invalid_telugu_file)

                # Empty the corresponding files in the cleaned folder
                open(cleaned_hindi_file, 'w').close()
                open(cleaned_telugu_file, 'w').close()

                # Track the modified folder
                modified_folders.append(folder_name)

        except Exception as e:
            print(f"Error processing folder {folder_name}: {e}")

# Print the folders where the files were emptied
if modified_folders:
    print(f"Cleared content of the following folders due to incorrect language detection: {', '.join(modified_folders)}")
else:
    print("No files were modified.")