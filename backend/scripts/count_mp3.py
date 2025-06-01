import os

mp3_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ai', 'assets', 'MP3-Example')
count = sum(len([f for f in files if f.endswith('.mp3')]) for _, _, files in os.walk(mp3_dir))
print(f"Total MP3 files: {count}") 