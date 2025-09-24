import re
from dataclasses import dataclass

@dataclass
class Subtitle:
    def __init__(self, index, start_time, end_time, text):
        self.index = index
        self.start_time = start_time
        self.end_time = end_time
        self.text = text

    def __eq__(self, other):
        # Two Subtitle objects are equal if their start, end times, and text are the same
        return (self.start_time == other.start_time and 
                self.end_time == other.end_time and 
                self.text == other.text)

    def __hash__(self):
        # Hash based on start_time, end_time, and text
        return hash((self.start_time, self.end_time, self.text))

    def __repr__(self):
        return f"Subtitle(start_time={self.start_time}, end_time={self.end_time}, text='{self.text}')"

def parse_time(time_str):
    hours, minutes, seconds = time_str.split(':')
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds.replace(',', '.'))

def parse_srt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    subtitle_blocks = re.split(r'\n\n+', content.strip())
    subtitles = []

    for block in subtitle_blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            index = int(lines[0])
            time_range = lines[1].split(' --> ')
            text = ' '.join(lines[2:])
            
            subtitle = Subtitle(
                index=index,
                start_time=parse_time(time_range[0]),
                end_time=parse_time(time_range[1]),
                text=text
            )
            subtitles.append(subtitle)

    return subtitles