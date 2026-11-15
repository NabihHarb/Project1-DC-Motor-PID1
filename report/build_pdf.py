"""Render report.html to report.pdf (needs Playwright + Chromium).
Alternative: open report.html in Chrome/Edge, Ctrl+P, 'Save as PDF', A4."""
from pathlib import Path
from playwright.sync_api import sync_playwright

here = Path(__file__).parent.resolve()
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page()
    page.goto((here / "report.html").as_uri())
    page.pdf(path=str(here / "report.pdf"), format="A4", prefer_css_page_size=True,
             print_background=True)
    b.close()
print("Wrote", here / "report.pdf")
