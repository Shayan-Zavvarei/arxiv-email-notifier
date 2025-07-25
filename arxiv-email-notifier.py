import arxiv
import subprocess
import json
from datetime import datetime, timedelta
import os

# Configuration
EMAIL_ADDRESS = "your_email@gmail.com" 
HISTORY_FILE = os.path.expanduser("~/arxiv_script/arxiv_history.json")

# Load or initialize history
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
else:
    history = {}

# Search parameters
search = arxiv.Search(
    query="cat:hep-ph OR cat:astro-ph.HE OR cat:nucl-th OR cat:quant-ph",
    max_results=50,
    sort_by=arxiv.Search.SORT_BY_SUBMITTED_DATE
)

results = list(search.results())

# Define a timezone-aware yesterday
tz = results[0].published.tzinfo if results else datetime.now().astimezone().tzinfo
yesterday = datetime.now(tz) - timedelta(days=1)

# Filter new papers
new_papers = [
    paper for paper in results
    if paper.published.astimezone(tz) > yesterday
    and any(cat in ['hep-ph', 'astro-ph.HE', 'nucl-th', 'quant-ph'] for cat in paper.categories)
    and paper.entry_id not in history
]

# Sort by date
new_papers.sort(key=lambda x: x.published, reverse=True)

# Email body
email_body = f"Number of new articles: {len(new_papers)}\n\n"
for i, paper in enumerate(new_papers, 1):
    email_body += f"Article {i}:\n"
    email_body += f"Title: {paper.title}\n"
    email_body += f"Published: {paper.published.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
    email_body += f"PDF Link: {paper.pdf_url}\n"
    email_body += f"Abstract: {paper.summary[:300]}...\n"
    email_body += f"Categories: {', '.join(paper.categories)}\n"
    email_body += f"Authors: {', '.join(str(author) for author in paper.authors)}\n\n"

if not new_papers:
    email_body += "No new articles found!\n"

# Send email
subject = f"New arXiv Articles - {datetime.now().strftime('%Y-%m-%d')}"
email_command = f'echo -e "Subject: {subject}\n\n{email_body}" | msmtp -a gmail {EMAIL_ADDRESS}'
subprocess.run(email_command, shell=True, text=True)

# Update history
for paper in new_papers:
    history[paper.entry_id] = paper.title

with open(HISTORY_FILE, "w") as f:
    json.dump(history, f, indent=2)