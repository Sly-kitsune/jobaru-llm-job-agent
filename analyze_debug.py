from bs4 import BeautifulSoup
import os

file_path = "applications/debug_html/apply_fail_204248.html"

if not os.path.exists(file_path):
    # Try finding the latest one if that specific one doesn't exist (unlikely)
    files = sorted([f for f in os.listdir("applications/debug_html") if f.startswith("apply_fail_")], reverse=True)
    if files:
        file_path = os.path.join("applications/debug_html", files[0])

print(f"Analyzing: {file_path}")

with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

print("\n--- BUTTONS ---")
buttons = soup.find_all("button")
for btn in buttons:
    text = btn.get_text(strip=True)
    classes = btn.get("class", [])
    aria = btn.get("aria-label", "")
    print(f"BUTTON | Text: '{text}' | Classes: {classes} | Aria: '{aria}'")

print("\n--- LINKS (Possible Apply Buttons) ---")
links = soup.find_all("a")
for link in links:
    text = link.get_text(strip=True)
    classes = link.get("class", [])
    href = link.get("href", "")
    if "apply" in text.lower() or "apply" in str(classes).lower():
        print(f"LINK | Text: '{text}' | Classes: {classes} | Href: '{href[:50]}...'")

print("\n--- SEARCH FOR 'APPLY' TEXT ---")
# Find any element containing "Apply"
for element in soup.find_all(string=lambda text: "apply" in text.lower() if text else False):
    parent = element.parent
    print(f"TEXT MATCH | Tag: {parent.name} | Text: '{element.strip()}' | Classes: {parent.get('class', [])}")
