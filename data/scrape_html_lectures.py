import requests
from bs4 import BeautifulSoup
import json
import time

headers = {"User-Agent": "Mozilla/5.0"}

def decode_data_array(data_array):
    """Decode SvelteKit's compressed reference format"""
    lectures = []
    for item in data_array:
        if isinstance(item, dict) and "lecturelink" in item:
            link_idx = item["lecturelink"]
            name_idx = item.get("name")
            link = data_array[link_idx] if isinstance(link_idx, int) else link_idx
            name = data_array[name_idx] if isinstance(name_idx, int) else name_idx
            if link and isinstance(link, str) and link.startswith("http"):
                lectures.append({"name": name, "url": link})
    return lectures

def get_html_lecture_text(url):
    """Scrape text from an HTML lecture page"""
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code != 200:
        raise Exception(f"HTTP {r.status_code}")
    soup = BeautifulSoup(r.text, "html.parser")
    
    # Remove navigation, scripts, styles
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    
    text = soup.get_text(separator=" ", strip=True)
    # Clean up extra whitespace
    import re
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Load all courses — filter to Web content type only
with open("textile_courses.json") as f:
    all_courses = json.load(f)

# Load already-processed video courses to skip them
with open("textile_courses_with_youtube.json") as f:
    video_courses = json.load(f)
video_ids = {c["course_id"] for c in video_courses}

# Get only the 14 older HTML courses
html_courses = [c for c in all_courses if c["course_id"] not in video_ids]
print(f"HTML courses to scrape: {len(html_courses)}")

all_lectures = []
failed = []

for course in html_courses:
    course_id = course["course_id"]
    print(f"\n📘 {course['title']}")
    
    # Get lecture list from __data.json
    data_url = f"https://nptel.ac.in/courses/{course_id}/__data.json"
    try:
        r = requests.get(data_url, headers=headers, timeout=10)
        data_array = r.json()["nodes"][1]["data"]
        lectures = decode_data_array(data_array)
        print(f"   Found {len(lectures)} lectures")
    except Exception as e:
        print(f"   ❌ Could not get lecture list: {e}")
        continue
    
    for lecture in lectures:
        try:
            text = get_html_lecture_text(lecture["url"])
            record = {
                "course_id":    course_id,
                "course_title": course["title"],
                "professor":    course["professor"],
                "institute":    course["institute"],
                "lecture_name": lecture["name"],
                "lecture_url":  lecture["url"],
                "content":      text,
                "word_count":   len(text.split())
            }
            all_lectures.append(record)
            print(f"   ✅ {lecture['name'][:50]} ({len(text.split())} words)")
        
        except Exception as e:
            print(f"   ❌ {lecture['name'][:50]}: {e}")
            failed.append({
                "course_id":    course_id,
                "lecture_name": lecture["name"],
                "url":          lecture["url"],
                "reason":       str(e)
            })
        
        time.sleep(0.5)

# Save
with open("textile_html_lectures.json", "w", encoding="utf-8") as f:
    json.dump(all_lectures, f, indent=2, ensure_ascii=False)

with open("html_failed.json", "w", encoding="utf-8") as f:
    json.dump(failed, f, indent=2, ensure_ascii=False)

total_words = sum(r["word_count"] for r in all_lectures)
print(f"\n{'='*50}")
print(f"✅ Lectures scraped: {len(all_lectures)}")
print(f"⚠️  Failed:          {len(failed)}")
print(f"📝 Total words:      {total_words:,}")
print(f"📁 Saved → textile_html_lectures.json")