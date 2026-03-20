import subprocess
import glob
import re
import os
import json
import time

COOKIES_PROFILE = "firefox:/home/kniting/snap/firefox/common/.mozilla/firefox/sfkzvvpe.default"
FIREFOX_PROFILE = COOKIES_PROFILE

def get_transcript(video_id, retries=3):
    output_path = f"/tmp/nptel_{video_id}"
    
    # Clean old files
    for f in glob.glob(f"{output_path}*"):
        os.remove(f)
    
    for attempt in range(retries):
        result = subprocess.run([
            "python", "-m", "yt_dlp",
            "--js-runtimes", "node:/usr/bin/node",
            "--cookies-from-browser", COOKIES_PROFILE,
            "--write-auto-sub",
            "--sub-lang", "en",
            "--sub-format", "vtt",
            "--format", "18",
            "--quiet",
            "-o", output_path,
            "--exec", "rm {}",
            f"https://www.youtube.com/watch?v={video_id}"
        ], capture_output=True, text=True, timeout=120)
        
        vtt_files = glob.glob(f"{output_path}*.vtt")
        
        if vtt_files:
            text = parse_vtt(vtt_files[0])
            os.remove(vtt_files[0])
            return text
        
        if "429" in result.stderr:
            wait = 60 * (attempt + 1)
            print(f"      Rate limited, waiting {wait}s...")
            time.sleep(wait)
        else:
            break
    
    raise Exception(result.stderr[-200:] if result.stderr else "No VTT file downloaded")

def parse_vtt(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Remove WEBVTT header
    content = re.sub(r'WEBVTT.*?\n\n', '', content, flags=re.DOTALL)
    # Remove timestamp lines
    content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}[^\n]*\n', '', content)
    # Remove HTML tags
    content = re.sub(r'<[^>]+>', '', content)
    # Deduplicate lines (VTT repeats lines)
    lines = content.split('\n')
    seen = set()
    unique = []
    for line in lines:
        line = line.strip()
        if line and line not in seen:
            seen.add(line)
            unique.append(line)
    
    return " ".join(unique)

# ── Main ───────────────────────────────────────────────────
with open("textile_courses_with_youtube.json") as f:
    courses = json.load(f)

all_transcripts = []
failed = []

for course in courses:
    print(f"\n📘 {course['title']}")
    
    for lecture in course["lectures"]:
        video_id = lecture["youtube_id"]
        
        try:
            text = get_transcript(video_id)
            record = {
                "course_id":    course["course_id"],
                "course_title": course["title"],
                "professor":    course["professor"],
                "institute":    course["institute"],
                "lecture_name": lecture["lecture_name"],
                "youtube_id":   video_id,
                "youtube_url":  lecture["youtube_url"],
                "transcript":   text,
                "word_count":   len(text.split())
            }
            all_transcripts.append(record)
            print(f"   ✅ {lecture['lecture_name']} ({len(text.split())} words)")
        
        except Exception as e:
            print(f"   ❌ {lecture['lecture_name']}: {str(e)[:80]}")
            failed.append({
                "video_id":     video_id,
                "lecture_name": lecture["lecture_name"],
                "reason":       str(e)[:200]
            })
        
        time.sleep(5)  # 5 second delay between videos

    # Save progress after each course
    with open("textile_transcripts.json", "w") as f:
        json.dump(all_transcripts, f, indent=2, ensure_ascii=False)

with open("failed_transcripts.json", "w") as f:
    json.dump(failed, f, indent=2, ensure_ascii=False)

total_words = sum(r["word_count"] for r in all_transcripts)
print(f"\n{'='*50}")
print(f"✅ Transcripts: {len(all_transcripts)}")
print(f"⚠️  Failed:     {len(failed)}")
print(f"📝 Total words: {total_words:,}")