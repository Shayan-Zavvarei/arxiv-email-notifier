# 📧 arXiv Daily Email Notification Script

*A lightweight Python script to automatically fetch daily arXiv papers from specified categories and email them to your Gmail inbox.*

---

##  Features

- **Automated arXiv Fetching**: Retrieves the latest arXiv papers based on custom categories.
- **Email Notifications**: Sends a daily summary of new articles to your Gmail inbox.
- **Customizable Categories**: Easily adjust which arXiv categories to monitor.
- **History Tracking**: Avoids duplicate notifications using a local history file.
- **Scheduled Execution**: Can be run automatically every day via a Cron job.

---

##  Prerequisites

| Requirement             | Description                                         |
|-------------------------|-----------------------------------------------------|
| Ubuntu | Your system must be running Ubuntu OS.             |
| Python 3                | Usually pre-installed.                              |
| Gmail Account           | Requires 2-Step Verification and an App Password.   |
| Internet Connection     | Required to fetch arXiv data and send emails.       |

---

##  Setup Guide

### 1. Python Environment

```bash
python3 -m venv ~/myenv
source ~/myenv/bin/activate
pip install arxiv
```
## 2. Project Setup
```bash
mkdir -p ~/arxiv_script
cd ~/arxiv_script
nano arxiv_email.py
```
Paste the script code into arxiv_email.py.
Make the script executable:
```bash
chmod +x ~/arxiv_script/arxiv_email.py
```
## 3. Configure Email Sending with msmtp
### 3.1 Install msmtp
```bash
sudo apt update
sudo apt install msmtp
```
### 3.2 Gmail Configuration
Go to Google Account Security Settings
Enable 2-Step Verification
Create an App Password under App Passwords
Save the 16-character password

### 3.3 Configure .msmtprc
```
nano ~/.msmtprc
```
Paste the following (replace placeholders with your info):
```
defaults
auth           on
tls            on
tls_trust_file /etc/ssl/certs/ca-certificates.crt
logfile        ~/.msmtp.log
account        gmail
host           smtp.gmail.com
port           456
from           your_email@gmail.com
user           your_email@gmail.com
password       xxxxxxxxxxxxxxxx
account default : gmail
```
Set correct permissions:
```
chmod 500 ~/.msmtprc
```
### 3.4 Test msmtp
```
echo -e "Subject: Test Email\n\nThis is a test from msmtp" | msmtp -a gmail your_email@gmail.com
```
## 4. Run the Script
```
python3 ~/arxiv_script/arxiv_email.py
```
You should receive an email with today's arXiv articles.

## 5. Schedule with Cron
### 5.1 Get Full Python Path
```
source ~/myenv/bin/activate
```
which python3
### 5.2 Edit Crontab
```
crontab -e
```
Add the following line (update Python path if needed):
```
0 8 * * * /home/user/myenv/bin/python3 ~/arxiv_script/arxiv_email.py >> ~/arxiv_script/cron.log 2>&1
```
Create the log file:
```
touch ~/arxiv_script/cron.log
chmod u+w ~/arxiv_script/cron.log
```
# Python Script
```
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
```
# Customization
| Config            | Description                                         |
|-------------------------|-----------------------------------------------------|
| query| Adjust categories or keywords for arXiv search            |
| max_results               | Limit number of articles fetched per day                              |
| EMAIL_ADDRESS           | Destination Gmail address   |
| timedelta(days=1)     | Time window for new papers (e.g., 12 hours, etc.)       |

## Built With
- Python 3
- arxiv Python library
- msmtp
- cron



















