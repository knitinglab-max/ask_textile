import requests
from bs4 import BeautifulSoup

# Test with one older course
url = "https://nptel.ac.in/courses/116102005"
headers = {"User-Agent": "Mozilla/5.0"}

r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, "html.parser")

print(f"Status: {r.status_code}")
print(f"Page size: {len(r.text)} chars")
print("\n--- All links on page ---")
for a in soup.find_all("a", href=True)[:30]:
    print(a["href"], "|", a.get_text(strip=True)[:50])