import requests
from bs4 import BeautifulSoup
import json

url = "https://nptel.ac.in/courses"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
}

response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}, Size: {len(response.text)} chars")

soup = BeautifulSoup(response.text, "html.parser")

# ── Target the exact class name we found in the HTML ──
# Every course lives inside a <div class="course-card ...">
course_cards = soup.find_all("div", class_="course-card")
print(f"Total course cards found: {len(course_cards)}")

textile_courses = []

for card in course_cards:
    # ── Extract discipline first — use it to filter ──
    discipline_tag = card.find("div", class_="discipline")
    if not discipline_tag:
        continue
    
    discipline = discipline_tag.get_text(strip=True)
    
    # ── Only keep Textile Engineering ──
    if discipline != "Textile Engineering":
        continue
    
    # ── Extract each field using its exact class name ──
    name_tag     = card.find("div", class_="name")
    meta_tag     = card.find("div", class_="meta-data")
    link_tag     = card.find("a", href=True)
    
    # Professor and institute are inside <span> tags in meta-data
    spans = meta_tag.find_all("span") if meta_tag else []
    professor = spans[0].get_text(strip=True) if len(spans) > 0 else ""
    institute = spans[1].get_text(strip=True) if len(spans) > 1 else ""
    
    course = {
        "course_id":  link_tag["href"].replace("/courses/", "") if link_tag else "",
        "url":        f"https://nptel.ac.in{link_tag['href']}" if link_tag else "",
        "title":      name_tag.get_text(strip=True) if name_tag else "",
        "discipline": discipline,
        "professor":  professor,
        "institute":  institute,
    }
    textile_courses.append(course)

print(f"\n✅ Textile Engineering courses found: {len(textile_courses)}")

# ── Save to JSON ──
with open("textile_courses.json", "w", encoding="utf-8") as f:
    json.dump(textile_courses, f, indent=2, ensure_ascii=False)

print("Saved → textile_courses.json")

# ── Preview ──
for c in textile_courses[:5]:
    print(f"\n→ {c['title']}")
    print(f"   ID: {c['course_id']}")
    print(f"   Prof: {c['professor']} | {c['institute']}")