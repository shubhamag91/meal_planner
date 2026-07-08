# -*- coding: utf-8 -*-
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
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


LOG_FILE = os.path.join(os.path.dirname(__file__), "run.log")

def setup_session_with_retries():
    """Create a requests session with retry strategy"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def log(msg):
    line = "[{}] {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), msg)
    print(line)

    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# -------- CONFIG --------
import os

NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
WIFE_EMAIL = os.environ.get("WIFE_EMAIL")
DATABASE_ID = os.environ.get("DATABASE_ID")

headers = {
    "Authorization": "Bearer {0}".format(NOTION_API_KEY),
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# -------- LOGGER --------
def log(msg):
    print("[{}] {}".format(datetime.now().strftime('%H:%M:%S'), msg))

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
    url = "https://api.notion.com/v1/databases/{0}/query".format(DATABASE_ID)
    session = setup_session_with_retries()
    try:
        response = session.post(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json().get("results", [])
    except requests.exceptions.RequestException as e:
        log("ERROR: Notion fetch failed after retries: {0}".format(str(e)))
        return []
    finally:
        session.close()

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

def get_recent_cuisine_penalty(dishes, lookback_days=3):
    """Calculate cuisine variety penalty based on recently eaten dishes"""
    from collections import Counter
    import datetime
    
    # Get recently eaten dishes (based on last_eaten)
    recent_dishes = []
    cutoff_date = datetime.now() - datetime.timedelta(days=lookback_days)
    
    for dish in dishes:
        if dish["last_eaten"]:
            try:
                last_eaten_date = datetime.datetime.fromisoformat(dish["last_eaten"])
                if last_eaten_date >= cutoff_date:
                    recent_dishes.append(dish)
            except:
                # If date parsing fails, skip this dish for variety calculation
                pass
    
    # Count cuisine types in recent dishes
    cuisine_counts = Counter()
    for dish in recent_dishes:
        cuisine = dish.get("cuisine", "Unknown")
        cuisine_counts[cuisine] += 1
    
    # If no recent dishes, return no penalty
    if not recent_dishes:
        return 0, {}
    
    # Calculate penalty: more repetition = higher penalty
    # Normalize by number of recent dishes to get repetition ratio
    total_recent = len(recent_dishes)
    max_repetition = max(cuisine_counts.values()) if cuisine_counts else 0
    repetition_ratio = max_repetition / float(total_recent) if total_recent > 0 else 0
    
    # Apply penalty: 0-5 points based on repetition
    # 0% repetition (perfect variety) = 0 penalty
    # 100% repetition (same cuisine always) = 5 point penalty
    variety_penalty = repetition_ratio * 5
    
    return variety_penalty, dict(cuisine_counts)

def get_seasonal_boost(dish):
    """Calculate seasonal boost based on current month and dish properties"""
    month = datetime.now().month  # 1-12
    
    # Define seasonal preferences (simplified)
    # Month groupings: Winter(12,1,2), Spring(3,4,5), Summer(6,7,8), Fall(9,10,11)
    seasonal_boost = 0
    
    # Light/cooling foods boost in spring/summer
    if month in [3,4,5,6,7,8]:  # Spring/Summer
        if "Light" in (dish.get("tags") or []):
            seasonal_boost += 1
        if dish.get("effort", 3) <= 2:  # Lower effort foods
            seasonal_boost += 0.5
        # Avoid heavy/comfort foods in hot months
        if "Heavy" in (dish.get("tags") or []):
            seasonal_boost -= 1
        if "Comfort" in (dish.get("tags") or []) and month in [6,7,8]:  # Peak summer
            seasonal_boost -= 0.5
            
    # Warm/comforting foods boost in fall/winter
    elif month in [9,10,11,12,1,2]:  # Fall/Winter
        if "Heavy" in (dish.get("tags") or []):
            seasonal_boost += 1
        if "Comfort" in (dish.get("tags") or []):
            seasonal_boost += 0.5
        if dish.get("effort", 3) >= 3:  # Higher effort cooking acceptable
            seasonal_boost += 0.5
        # Light foods less preferred in cold months
        if "Light" in (dish.get("tags") or []) and month in [12,1,2]:  # Deep winter
            seasonal_boost -= 0.5
    
    return seasonal_boost

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

    # Add randomness for variety
    score += random.uniform(-1, 1)
    
    # TODO: These will be calculated in recommend_meals where we have access to full dish list
    # For now, return base score - enhancements will be added later
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

def get_top_n_enhanced(dishes, meal_type, used, n=3):
    """Get top N dishes using enhanced score"""
    candidates = [d for d in dishes if d["meal"] == meal_type and d["name"] not in used]
    candidates.sort(key=lambda x: x["enhanced_score"], reverse=True)
    random.shuffle(candidates[:5])
    return candidates[:n]

# -------- NOTIFICATIONS --------
def send_notification(plan_text, channel="email"):
    """Send notification via specified channel"""
    if channel == "email":
        return send_email(plan_text)
    elif channel == "whatsapp":
        return send_whatsapp(plan_text)
    elif channel == "smart_display":
        return send_smart_display(plan_text)
    else:
        log("ERROR: Unknown notification channel: {0}".format(channel))
        return False

def send_email(plan_text):
    msg = MIMEText(plan_text, "plain", "utf-8")
    msg["Subject"] = "Meal Plan"
    msg["From"] = SENDER_EMAIL
    msg["To"] = WIFE_EMAIL

    max_retries = 3
    for attempt in range(max_retries):
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as s:
                s.starttls()
                s.login(SENDER_EMAIL, EMAIL_PASSWORD)
                s.send_message(msg)
            log("SUCCESS: Email sent")
            return True
        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                log("ERROR: Email failed after {0} attempts: {1}".format(max_retries, e))
                return False
            else:
                wait_time = 2 ** attempt  # Exponential backoff
                log("WARNING: Email attempt {0} failed, retrying in {1}s: {2}".format(attempt + 1, wait_time, e))
                time.sleep(wait_time)
    return False

def send_whatsapp(plan_text):
    """Send WhatsApp notification (placeholder for Twilio integration)"""
    # TODO: Implement Twilio WhatsApp API integration
    # Requires: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER
    log("INFO: WhatsApp notification would be sent: {0}...".format(plan_text[:50]))
    log("WARNING: WhatsApp functionality not yet implemented")
    return True  # Return True to not break flow during development

def send_smart_display(plan_text):
    """Send notification to smart display (HTML file for kitchen tablet)"""
    try:
        # Create a simple HTML file that can be displayed on a kitchen tablet
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Today's Meal Plan</title>
            <meta http-equiv="refresh" content="300"> <!-- Refresh every 5 minutes -->
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; text-align: center; }
                .meal-type { margin: 20px 0; padding: 15px; background: #ecf0f1; border-left: 4px solid #3498db; }
                .meal-type h2 { color: #2c3e50; margin-top: 0; }
                .meal-item { padding: 8px 0; border-bottom: 1px solid #bdc3c7; }
                .meal-item:last-child { border-bottom: none; }
                .footer { text-align: center; margin-top: 30px; color: #7f8c8d; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🍽️ Today's Meal Plan</h1>
                <p><em>Updated: {0}</em></p>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Parse the plan text to extract meals
        lines = plan_text.split('\n')
        current_meal_type = None
        
        for line in lines:
            if line.startswith('Breakfast:'):
                current_meal_type = 'Breakfast'
                html_content += '<div class="meal-type"><h2>🥣 Breakfast</h2>'
            elif line.startswith('Lunch:'):
                current_meal_type = 'Lunch'
                html_content += '</div><div class="meal-type"><h2>🍛 Lunch</h2>'
            elif line.startswith('Dinner:'):
                current_meal_type = 'Dinner'
                html_content += '</div><div class="meal-type"><h2>🍽️ Dinner</h2>'
            elif line.startswith('B') or line.startswith('L') or line.startswith('D'):
                # Skip the reply instruction line
                continue
            elif line.strip() and not line.startswith('Meal Suggestions') and not line.startswith('Reply:'):
                # This is a meal item
                if current_meal_type:
                    # Clean up the line (remove B1., L2., D3. prefixes)
                    clean_line = line.strip()
                    if len(clean_line) > 2 and clean_line[1] == '.':
                        clean_line = clean_line[3:].strip()
                    html_content += '<div class="meal-item">• {0}</div>'.format(clean_line)
        
        html_content += """
                </div>
                <div class="footer">
                    This meal plan updates automatically. Check back for tomorrow's suggestions!
                </div>
            </div>
        </body>
        </html>
        """
        
        # Write to file
        dashboard_path = os.path.join(os.path.dirname(__file__), "meal_plan_dashboard.html")
        with open(dashboard_path, "w") as f:
            f.write(html_content)
            
        log("SUCCESS: Smart display dashboard updated: {0}".format(dashboard_path))
        return True
        
    except Exception as e:
        log("ERROR: Failed to update smart display: {0}".format(e))
        return False

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

    q = 'is:unread from:{0} subject:"Meal Plan"'.format(WIFE_EMAIL)
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
        log("[WARNING] No options file")
        return

    with open("today_options.json") as f:
        options = json.load(f)

    clean = extract_clean_reply(text)

    if not clean:
        log("[ERROR] No valid reply found")
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
        log("[ERROR] No valid selections")
        return

    log("SUCCESS: Selected: {0}".format(selected))
    update_last_eaten(selected)

# -------- NOTION UPDATE --------
def update_last_eaten(names):
    today = datetime.now().date().isoformat()
    results = fetch_dishes()
    session = setup_session_with_retries()
    try:
        for item in results:
            name = get_value(item["properties"]["Dish Name"], "title")

            if name in names:
                url = "https://api.notion.com/v1/pages/{0}".format(item['id'])
                try:
                    response = session.patch(url, headers=headers, json={
                        "properties": {
                            "Last Eaten": {"date": {"start": today}}
                        }
                    })
                    response.raise_for_status()
                    log("Updated {0}".format(name))
                except requests.exceptions.RequestException as e:
                    log("[ERROR] Failed to update {0}: {1}".format(name, str(e)))
    finally:
        session.close()

# -------- PROCESS EMAILS --------
def process_email_replies():
    service = get_gmail_service()
    replies = read_replies()

    for msg_id, body in replies:
        log("INFO: Reply: {0}".format(body))
        process_reply(body)

        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()

# -------- MAIN --------
def recommend_meals():
    dishes = parse_dishes(fetch_dishes())
    
    # Apply enhancements to scoring
    enhanced_dishes = []
    for dish in dishes:
        enhanced_dish = dish.copy()
        
        # Get variety penalty
        variety_penalty, cuisine_counts = get_recent_cuisine_penalty(dishes, lookback_days=3)
        
        # Get seasonal boost
        seasonal_boost = get_seasonal_boost(dish)
        
        # Apply enhancements to base score
        base_score = compute_score(dish)
        enhanced_score = base_score - variety_penalty + seasonal_boost
        
        # Add some randomness to prevent exact ties
        enhanced_score += random.uniform(-0.5, 0.5)
        
        enhanced_dish["base_score"] = base_score
        enhanced_dish["variety_penalty"] = variety_penalty
        enhanced_dish["seasonal_boost"] = seasonal_boost
        enhanced_dish["enhanced_score"] = enhanced_score
        enhanced_dishes.append(enhanced_dish)
    
    # Sort by enhanced score
    enhanced_dishes.sort(key=lambda x: x["enhanced_score"], reverse=True)
    
    used = set()
    b = get_top_n_enhanced(enhanced_dishes, "Breakfast", used)
    used.update([x["name"] for x in b])

    l = get_top_n_enhanced(enhanced_dishes, "Lunch", used)
    used.update([x["name"] for x in l])

    d = [x for x in enhanced_dishes if x["meal"] == "Dinner" and x["name"] not in used]

    # For dinner, if lunch has heavy items, prefer lighter options
    if any(is_heavy(x) for x in l):
        d.sort(key=lambda x: (not is_light(x), -x["enhanced_score"]))
    else:
        d.sort(key=lambda x: -x["enhanced_score"])

    random.shuffle(d[:5])
    d = d[:3]

    # Log scoring details for debugging
    log_info = []
    for dish in b + l + d:
        log_info.append("{0}: base={1:.1f}, variety_penalty={2:.1f}, seasonal={3:.1f}, final={4:.1f}".format(
            dish["name"], 
            dish["base_score"], 
            dish["variety_penalty"], 
            dish["seasonal_boost"], 
            dish["enhanced_score"]
        ))
    log("Scoring details: " + " | ".join(log_info))

    text = "Meal Suggestions\n\nReply: B1 L2 D3\n\n"

    breakfast_lines = []
    for i, x in enumerate(b):
        breakfast_lines.append("B{0}. {1}".format(i+1, x['name']))
    text += "Breakfast:\n" + "\n".join(breakfast_lines)
    lunch_lines = []
    for i, x in enumerate(l):
        lunch_lines.append("L{0}. {1}".format(i+1, x['name']))
    text += "\n\nLunch:\n" + "\n".join(lunch_lines)
    dinner_lines = []
    for i, x in enumerate(d):
        dinner_lines.append("D{0}. {1}".format(i+1, x['name']))
    text += "\n\nDinner:\n" + "\n".join(dinner_lines)

    log(text)
    # Send notifications via multiple channels
    send_notification(text, channel="email")
    send_notification(text, channel="whatsapp") 
    send_notification(text, channel="smart_display")
    save_today_options(b, l, d)

# -------- RUN --------
if __name__ == "__main__":
    if should_send_today():
        log("INFO: Sending meals")
        recommend_meals()

    log("INFO: Checking replies")
    process_email_replies()