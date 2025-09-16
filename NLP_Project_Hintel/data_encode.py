import os
import chardet

# === CONFIGURATION ===
SOURCE_BASE_DIR = r'D:\SEMESTER_5\NLP_M2025\HIntel\NLP_Project_Hintel\data'       # Source folder (raw .srt files)
DEST_BASE_DIR   = r'D:\SEMESTER_5\NLP_M2025\HIntel\NLP_Project_Hintel\data_encode'  # Destination folder (UTF-8 encoded files)


def detect_encoding(file_path):
    """Detect file encoding using chardet."""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
    return result['encoding']


def convert_to_utf8(source_path, dest_path, src_encoding):
    """Convert a single file to UTF-8 encoding."""
    try:
        with open(source_path, 'r', encoding=src_encoding or 'utf-8-sig', errors='replace') as src_file:
            content = src_file.read()

        with open(dest_path, 'w', encoding='utf-8') as dest_file:
            dest_file.write(content)

        print(f"✅ Converted: {os.path.basename(source_path)} → UTF-8")
    except Exception as e:
        print(f"❌ Error converting {source_path}: {e}")


def process_folder(source_folder, dest_folder):
    """Process all .srt files in a single folder."""
    os.makedirs(dest_folder, exist_ok=True)
    srt_files = [f for f in os.listdir(source_folder) if f.endswith('.srt')]

    if not srt_files:
        print(f"⚠️ No .srt files found in: {source_folder}")
        return

    for file_name in srt_files:
        source_path = os.path.join(source_folder, file_name)
        dest_path = os.path.join(dest_folder, file_name)

        print(f"\nProcessing file: {file_name}")
        encoding = detect_encoding(source_path)
        print(f"Detected encoding: {encoding}")

        convert_to_utf8(source_path, dest_path, encoding)


def main():
    """Main function to walk through all data folders and convert files."""
    if not os.path.exists(SOURCE_BASE_DIR):
        print(f"❌ Source folder not found: {SOURCE_BASE_DIR}")
        return

    os.makedirs(DEST_BASE_DIR, exist_ok=True)

    for folder_name in os.listdir(SOURCE_BASE_DIR):
        source_folder = os.path.join(SOURCE_BASE_DIR, folder_name)

        if os.path.isdir(source_folder) and folder_name.startswith('data-'):
            dest_folder = os.path.join(DEST_BASE_DIR, folder_name)
            print(f"\n📂 Processing folder: {folder_name}")
            process_folder(source_folder, dest_folder)

    print("\n🎉 All .srt files have been converted to UTF-8 and saved in:")
    print(f"   {DEST_BASE_DIR}")


# === RUN SCRIPT ===
if __name__ == '__main__':
    main()
