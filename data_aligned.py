import os
import re
from srt_parser import parse_srt, Subtitle
from dtaidistance import dtw


def time_based_alignment(hindi_subs, telugu_subs, threshold=0.5):
    aligned_pairs = []
    for h_sub in hindi_subs:
        for t_sub in telugu_subs:
            overlap = max(0, min(h_sub.end_time, t_sub.end_time) - max(h_sub.start_time, t_sub.start_time))
            total_duration = max(h_sub.end_time, t_sub.end_time) - min(h_sub.start_time, t_sub.start_time)
            if total_duration > 0 and overlap / total_duration > threshold:
                aligned_pairs.append((h_sub, t_sub))
    return aligned_pairs

def length_based_refinement(aligned_pairs, max_length_diff=0.25):
    refined_pairs = []
    for h_sub, t_sub in aligned_pairs:
        max_length = max(len(h_sub.text), len(t_sub.text))
        if max_length > 0 and abs(len(h_sub.text) - len(t_sub.text)) / max_length <= max_length_diff:
            refined_pairs.append((h_sub, t_sub))
    return refined_pairs

def dtw_alignment(unaligned_hindi, unaligned_telugu):
    if not unaligned_hindi or not unaligned_telugu:
        return []

    hindi_lengths = [len(sub.text) for sub in unaligned_hindi]
    telugu_lengths = [len(sub.text) for sub in unaligned_telugu]
    
    alignment = dtw.warping_path(hindi_lengths, telugu_lengths)
    
    dtw_pairs = [(unaligned_hindi[i], unaligned_telugu[j]) for i, j in alignment]
    return dtw_pairs

def score_alignment(hindi_sub, telugu_sub):
    time_overlap = max(0, min(hindi_sub.end_time, telugu_sub.end_time) - max(hindi_sub.start_time, telugu_sub.start_time))
    total_duration = max(hindi_sub.end_time, telugu_sub.end_time) - min(hindi_sub.start_time, telugu_sub.start_time)
    time_score = time_overlap / total_duration if total_duration > 0 else 0
    
    max_length = max(len(hindi_sub.text), len(telugu_sub.text))
    length_score = 1 - abs(len(hindi_sub.text) - len(telugu_sub.text)) / max_length if max_length > 0 else 0
    return 0.6 * time_score + 0.4 * length_score

def final_alignment(time_based_pairs, length_refined_pairs, dtw_pairs):
    all_pairs = time_based_pairs + length_refined_pairs + dtw_pairs
    scored_pairs = [(pair, score_alignment(*pair)) for pair in all_pairs]
    scored_pairs.sort(key=lambda x: x[1], reverse=True)
    
    final_pairs = []
    used_hindi = set()
    used_telugu = set()
    
    for (h_sub, t_sub), score in scored_pairs:
        if h_sub not in used_hindi and t_sub not in used_telugu:
            final_pairs.append((h_sub, t_sub))
            used_hindi.add(h_sub)
            used_telugu.add(t_sub)
    
    return final_pairs

def align_subtitles(hindi_subs, telugu_subs):
    time_based_pairs = time_based_alignment(hindi_subs, telugu_subs)
    length_refined_pairs = length_based_refinement(time_based_pairs)
    
    aligned_hindi = set(pair[0] for pair in length_refined_pairs)
    aligned_telugu = set(pair[1] for pair in length_refined_pairs)
    unaligned_hindi = [sub for sub in hindi_subs if sub not in aligned_hindi]
    unaligned_telugu = [sub for sub in telugu_subs if sub not in aligned_telugu]
    
    dtw_pairs = dtw_alignment(unaligned_hindi, unaligned_telugu)
    final_pairs = final_alignment(time_based_pairs, length_refined_pairs, dtw_pairs)
    
    return final_pairs

def main():
    source_base_dir = 'data_deaccented'
    destination_base_dir = 'data_aligned'

    os.makedirs(destination_base_dir, exist_ok=True)

    for folder_name in os.listdir(source_base_dir):
        folder_path = os.path.join(source_base_dir, folder_name)
        
        if os.path.isdir(folder_path) and folder_name.startswith('data-'):
            print(f"\nProcessing folder: {folder_name}")
            
            # Find all Hindi and Telugu subtitle files in the folder
            hindi_files = [f for f in os.listdir(folder_path) if f.startswith('hin-') and f.endswith('.srt')]
            telugu_files = [f for f in os.listdir(folder_path) if f.startswith('tel-') and f.endswith('.srt')]
            
            # Sort the files to ensure matching pairs
            hindi_files.sort()
            telugu_files.sort()
            
            # Process each pair of files
            for hindi_file, telugu_file in zip(hindi_files, telugu_files):
                hindi_path = os.path.join(folder_path, hindi_file)
                telugu_path = os.path.join(folder_path, telugu_file)
                
                print(f"Aligning: {hindi_file} and {telugu_file}")
                
                hindi_subs = parse_srt(hindi_path)
                telugu_subs = parse_srt(telugu_path)
                
                aligned_pairs = align_subtitles(hindi_subs, telugu_subs)
                
                # Extract the number from the filename (e.g., 'hin-1.srt' -> '1')
                file_number = re.search(r'-(\d+)\.srt', hindi_file).group(1)
                
                dest_file_path = os.path.join(destination_base_dir, f'{folder_name}_aligned_{file_number}.tsv')
                with open(dest_file_path, 'w', encoding='utf-8') as f:
                    for hindi_sub, telugu_sub in aligned_pairs:
                        f.write(f"{hindi_sub.text}\t{telugu_sub.text}\n")
                
                print(f"Aligned subtitles saved to: {dest_file_path}")
            
            if not hindi_files or not telugu_files:
                print(f"No matching subtitle files found in folder: {folder_name}")

    print("\nAlignment process completed.")

if __name__ == "__main__":
    main()