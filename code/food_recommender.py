import re
import sys
import requests
import random
from datetime import datetime, date
import smtplib
from email.mime.text import MIMEText
import json
import base64
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


LOG_FILE = os.path.join(os.path.dirname(__file__), "run.log")

def log(msg):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)

    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# -------- CONFIG --------
NOTION_API_KEY = "***REMOVED_NOTION_TOKEN***"
EMAIL_PASSWORD = "***REMOVED_EMAIL_PASSWORD***"
SENDER_EMAIL = "shubhamag91@gmail.com"
WIFE_EMAIL = "rudrakshharlalka@gmail.com"
DATABASE_ID = "33be3817-a4e2-816d-a57d-f051463d5269"

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# -------- LOGGER --------
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# -------- SEND ONCE PER DAY --------
def should_send_today():
    today = date.today().isoformat()

    if os.path.exists("last_sent.txt"):
        with open("last_sent.txt", "r") as f:
            if f.read().strip() == today:
                return False

    with open("last_sent.txt", "w") as f:
        f.write(today)

    return True

# -------- FETCH DISHES --------
def fetch_dishes():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=headers)

    if response.status_code != 200:
        log(f"❌ Notion fetch failed: {response.text}")
        return []

    return response.json().get("results", [])

# -------- PARSE --------
def get_value(prop, type_):
    if type_ == "title":
        return prop["title"][0]["plain_text"] if prop["title"] else ""
    if type_ == "select":
        return prop["select"]["name"] if prop["select"] else None
    if type_ == "multi_select":
        return [x["name"] for x in prop["multi_select"]]
    if type_ == "number":
        return prop["number"] or 0
    if type_ == "date":
        return prop["date"]["start"] if prop["date"] else None
    return None

def compute_score(dish):
    score = (dish["your_rating"] + dish["wife_rating"]) * 2

    if dish["last_eaten"]:
        days = (datetime.now() - datetime.fromisoformat(dish["last_eaten"])).days
    else:
        days = 999

    score += days / 2

    if days <= 2:
        score -= 10
    elif days <= 5:
        score -= 5

    if dish["effort"] >= 4:
        score -= 2

    score += random.uniform(-1, 1)

    return score

def parse_dishes(results):
    dishes = []

    for item in results:
        props = item["properties"]

        dish = {
            "name": get_value(props["Dish Name"], "title"),
            "meal": get_value(props["Meal Type"], "select"),
            "effort": get_value(props["Effort"], "number"),
            "your_rating": get_value(props["Your Rating"], "number"),
            "wife_rating": get_value(props["Wife Rating"], "number"),
            "tags": get_value(props["Tags"], "multi_select"),
            "last_eaten": get_value(props["Last Eaten"], "date")
        }

        dish["score"] = compute_score(dish)
        dishes.append(dish)

    return dishes

# -------- HELPERS --------
def is_heavy(d): return "Heavy" in (d["tags"] or []) or d["effort"] >= 4
def is_light(d): return "Light" in (d["tags"] or []) or d["effort"] <= 2

def get_top_n(dishes, meal_type, used, n=3):
    candidates = [d for d in dishes if d["meal"] == meal_type and d["name"] not in used]
    candidates.sort(key=lambda x: x["score"], reverse=True)
    random.shuffle(candidates[:5])
    return candidates[:n]

# -------- EMAIL --------
def send_email(plan_text):
    msg = MIMEText(plan_text, "plain", "utf-8")
    msg["Subject"] = "Meal Plan"
    msg["From"] = SENDER_EMAIL
    msg["To"] = WIFE_EMAIL

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.starttls()
            s.login(SENDER_EMAIL, EMAIL_PASSWORD)
            s.send_message(msg)
        log("✅ Email sent")
    except Exception as e:
        log(f"❌ Email error: {e}")

# -------- SAVE OPTIONS --------
def save_today_options(b, l, d):
    with open("today_options.json", "w") as f:
        json.dump({
            "breakfast": [x["name"] for x in b],
            "lunch": [x["name"] for x in l],
            "dinner": [x["name"] for x in d]
        }, f)

# -------- GMAIL --------
def get_gmail_service():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(BASE_DIR, "token.json")
    cred_path = os.path.join(BASE_DIR, "credentials.json")

    creds = None

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # 🔥 KEY FIX: handle refresh properly
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    elif not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
        creds = flow.run_local_server(port=0)

    # Save updated creds
    with open(token_path, "w") as token:
        token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def read_replies():
    service = get_gmail_service()

    q = f'is:unread from:{WIFE_EMAIL} subject:"Meal Plan"'
    results = service.users().messages().list(userId='me', q=q).execute()

    messages = results.get('messages', [])
    replies = []

    for msg in messages:
        data = service.users().messages().get(userId='me', id=msg['id']).execute()

        if 'UNREAD' not in data['labelIds']:
            continue

        payload = data['payload']
        body = ""

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode()
        else:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode()

        replies.append((msg['id'], body))

    return replies

# -------- PROCESS REPLY --------
def extract_clean_reply(text):
    lines = text.strip().split("\n")

    for line in lines:
        line = line.strip()

        # Match: B1 L2 D3 format only
        if re.match(r'^[BLD]\d(\s+[BLD]\d)*$', line.upper()):
            return line

    return None


def process_reply(text):
    if not os.path.exists("today_options.json"):
        log("⚠️ No options file")
        return

    with open("today_options.json") as f:
        options = json.load(f)

    clean = extract_clean_reply(text)

    if not clean:
        log("❌ No valid reply found")
        return

    selected = []
    matches = re.findall(r'([BLD])(\d)', clean.upper())

    for cat, idx in matches:
        i = int(idx) - 1

        try:
            if cat == "B" and i < len(options["breakfast"]):
                selected.append(options["breakfast"][i])
            elif cat == "L" and i < len(options["lunch"]):
                selected.append(options["lunch"][i])
            elif cat == "D" and i < len(options["dinner"]):
                selected.append(options["dinner"][i])
        except:
            pass

    if not selected:
        log("❌ No valid selections")
        return

    log(f"✅ Selected: {selected}")
    update_last_eaten(selected)

# -------- NOTION UPDATE --------
def update_last_eaten(names):
    today = datetime.now().date().isoformat()
    results = fetch_dishes()

    for item in results:
        name = get_value(item["properties"]["Dish Name"], "title")

        if name in names:
            url = f"https://api.notion.com/v1/pages/{item['id']}"
            requests.patch(url, headers=headers, json={
                "properties": {
                    "Last Eaten": {"date": {"start": today}}
                }
            })
            log(f"Updated {name}")

# -------- PROCESS EMAILS --------
def process_email_replies():
    service = get_gmail_service()
    replies = read_replies()

    for msg_id, body in replies:
        log(f"📩 Reply: {body}")
        process_reply(body)

        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()

# -------- MAIN --------
def recommend_meals():
    dishes = parse_dishes(fetch_dishes())
    used = set()

    b = get_top_n(dishes, "Breakfast", used)
    used.update([x["name"] for x in b])

    l = get_top_n(dishes, "Lunch", used)
    used.update([x["name"] for x in l])

    d = [x for x in dishes if x["meal"] == "Dinner" and x["name"] not in used]

    if any(is_heavy(x) for x in l):
        d.sort(key=lambda x: (not is_light(x), -x["score"]))
    else:
        d.sort(key=lambda x: -x["score"])

    random.shuffle(d[:5])
    d = d[:3]

    text = "🍽️ Meal Suggestions\n\nReply: B1 L2 D3\n\n"

    text += "🥣 Breakfast:\n" + "\n".join([f"B{i+1}. {x['name']}" for i, x in enumerate(b)])
    text += "\n\n🍛 Lunch:\n" + "\n".join([f"L{i+1}. {x['name']}" for i, x in enumerate(l)])
    text += "\n\n🍽️ Dinner:\n" + "\n".join([f"D{i+1}. {x['name']}" for i, x in enumerate(d)])

    log(text)
    send_email(text)
    save_today_options(b, l, d)

# -------- RUN --------
if __name__ == "__main__":
    if should_send_today():
        log("📤 Sending meals")
        recommend_meals()

    log("📥 Checking replies")
    process_email_replies()