import requests
from bs4 import BeautifulSoup

url = "https://onlinecourses.nptel.ac.in/noc21_te11/unit?unit=11&lesson=12"
headers = {"User-Agent": "Mozilla/5.0"}

r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, "html.parser")

# Print page title
print("Title:", soup.title.string if soup.title else "None")

# Print all text content
print("\nPage text preview:")
print(soup.get_text()[:3000])