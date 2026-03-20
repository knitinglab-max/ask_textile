import requests
import json
import time

# Load our 29 courses from Step 1
with open("textile_courses.json", "r") as f:
    courses = json.load(f)

def extract_data_from_json(raw_data):
    """
    The __data.json uses a compressed reference format.
    The 'data' array contains all values.
    Objects reference positions in this array by index.
    We need to decode this structure.
    """
    nodes = raw_data.get("nodes", [])
    
    # Node 1 contains the actual course data
    if len(nodes) < 2 or not nodes[1]:
        return None
    
    data_array = nodes[1].get("data", [])
    if not data_array:
        return None
    
    # The data array uses index references
    # data[0] = {"courseOutline": 1} → courseOutline is at index 1
    # data[1] = {"nocCourse":2, "title":3, ...} → title is at index 3
    # data[3] = "Yarn manufacture I..." → the actual title string
    
    # Extract all youtube_ids and their lecture names
    lectures = []
    for i, item in enumerate(data_array):
        if isinstance(item, dict) and "youtube_id" in item:
            yt_index = item["youtube_id"]
            name_index = item.get("name")
            
            youtube_id = data_array[yt_index] if isinstance(yt_index, int) else yt_index
            name = data_array[name_index] if isinstance(name_index, int) else name_index
            
            lectures.append({
                "lecture_name": name,
                "youtube_id": youtube_id,
                "youtube_url": f"https://www.youtube.com/watch?v={youtube_id}"
            })
    
    # Extract title and professor
    title, professor, institute = "", "", ""
    for i, item in enumerate(data_array):
        if isinstance(item, dict) and "title" in item:
            t_idx = item["title"]
            title = data_array[t_idx] if isinstance(t_idx, int) else t_idx
        if isinstance(item, dict) and "professor" in item:
            p_idx = item["professor"]
            professor = data_array[p_idx] if isinstance(p_idx, int) else p_idx
        if isinstance(item, dict) and "instituteName" in item:
            i_idx = item["instituteName"]
            institute = data_array[i_idx] if isinstance(i_idx, int) else i_idx
    
    return {
        "title": title,
        "professor": professor,
        "institute": institute,
        "lectures": lectures
    }

# ── Main loop ──────────────────────────────────────────────
all_results = []
headers = {"User-Agent": "Mozilla/5.0"}

for course in courses:
    course_id = course["course_id"]
    url = f"https://nptel.ac.in/courses/{course_id}/__data.json"
    
    print(f"Fetching: {course['title'][:50]}...")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            raw = response.json()
            extracted = extract_data_from_json(raw)
            
            if extracted and extracted["lectures"]:
                result = {
                    "course_id": course_id,
                    "title": extracted["title"] or course["title"],
                    "professor": extracted["professor"] or course["professor"],
                    "institute": extracted["institute"] or course["institute"],
                    "lecture_count": len(extracted["lectures"]),
                    "lectures": extracted["lectures"]
                }
                all_results.append(result)
                print(f"  ✅ {len(extracted['lectures'])} lectures found")
            else:
                print(f"  ⚠️  No lectures (may be older non-video course)")
        else:
            print(f"  ❌ Status: {response.status_code}")
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    time.sleep(0.5)  # be polite, 0.5s between requests

# ── Save results ───────────────────────────────────────────
with open("textile_courses_with_youtube.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

# ── Summary ───────────────────────────────────────────────
total_lectures = sum(c["lecture_count"] for c in all_results)
print(f"\n{'='*50}")
print(f"Courses with videos: {len(all_results)}/{len(courses)}")
print(f"Total lectures:      {total_lectures}")
print(f"Saved → textile_courses_with_youtube.json")