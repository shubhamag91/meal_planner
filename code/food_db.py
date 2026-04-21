import requests
import os

NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
DATABASE_ID = os.environ.get("DATABASE_ID")

url = "https://api.notion.com/v1/pages"

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

dishes = [

    # -------- BREAKFAST --------
    {"name": "Poha", "meal": "Breakfast", "cuisine": "Mix", "effort": 2, "tags": ["Quick", "Light"]},
    {"name": "Upma", "meal": "Breakfast", "cuisine": "South Indian", "effort": 2, "tags": ["Quick"]},
    {"name": "Idli Sambar", "meal": "Breakfast", "cuisine": "South Indian", "effort": 3, "tags": ["Light"]},
    {"name": "Masala Dosa", "meal": "Breakfast", "cuisine": "South Indian", "effort": 4, "tags": ["Comfort"]},
    {"name": "Paneer Paratha", "meal": "Breakfast", "cuisine": "North Indian", "effort": 4, "tags": ["Heavy", "Comfort"]},
    {"name": "Aloo Paratha", "meal": "Breakfast", "cuisine": "North Indian", "effort": 4, "tags": ["Heavy"]},
    {"name": "Besan Chilla", "meal": "Breakfast", "cuisine": "North Indian", "effort": 2, "tags": ["Quick"]},
    {"name": "Moong Dal Chilla", "meal": "Breakfast", "cuisine": "North Indian", "effort": 2, "tags": ["Light"]},
    {"name": "Oats Chilla", "meal": "Breakfast", "cuisine": "Mix", "effort": 2, "tags": ["Light"]},
    {"name": "Vegetable Sandwich", "meal": "Breakfast", "cuisine": "Mix", "effort": 1, "tags": ["Quick"]},
    {"name": "Methi Thepla", "meal": "Breakfast", "cuisine": "Mix", "effort": 3, "tags": ["Light"]},
    {"name": "Sabudana Khichdi", "meal": "Breakfast", "cuisine": "Mix", "effort": 3, "tags": ["Light"]},
    {"name": "Dhokla", "meal": "Breakfast", "cuisine": "Mix", "effort": 3, "tags": ["Light"]},
    {"name": "Rava Dosa", "meal": "Breakfast", "cuisine": "South Indian", "effort": 3, "tags": ["Light"]},
    {"name": "Plain Paratha + Curd", "meal": "Breakfast", "cuisine": "North Indian", "effort": 2, "tags": ["Comfort"]},
    {"name": "Namkeen Jave (Vermicelli)", "meal": "Breakfast", "cuisine": "North Indian", "effort": 2, "tags": ["Quick", "Light"]},
    {"name": "Dahi Chura", "meal": "Breakfast", "cuisine": "North Indian", "effort": 1, "tags": ["Quick", "Light"]},
    {"name": "Roti Churi", "meal": "Breakfast", "cuisine": "Mix", "effort": 1, "tags": ["Quick"]},

    # -------- LUNCH --------
    {"name": "Rajma Chawal", "meal": "Lunch", "cuisine": "North Indian", "effort": 3, "tags": ["Comfort"]},
    {"name": "Chole", "meal": "Lunch", "cuisine": "North Indian", "effort": 3, "tags": ["Comfort"]},
    {"name": "Dal Tadka Rice", "meal": "Lunch", "cuisine": "North Indian", "effort": 2, "tags": ["Light"]},
    {"name": "Kadhi Chawal", "meal": "Lunch", "cuisine": "North Indian", "effort": 3, "tags": ["Light"]},
    {"name": "Paneer Butter Masala", "meal": "Lunch", "cuisine": "North Indian", "effort": 4, "tags": ["Heavy", "Comfort"]},
    {"name": "Shahi Paneer", "meal": "Lunch", "cuisine": "North Indian", "effort": 4, "tags": ["Heavy"]},
    {"name": "Dal Makhani", "meal": "Lunch", "cuisine": "North Indian", "effort": 4, "tags": ["Heavy", "Comfort"]},
    {"name": "Vegetable Pulao", "meal": "Lunch", "cuisine": "Mix", "effort": 2, "tags": ["Light"]},
    {"name": "Jeera Rice + Dal", "meal": "Lunch", "cuisine": "North Indian", "effort": 2, "tags": ["Light"]},
    {"name": "Curd Rice", "meal": "Lunch", "cuisine": "South Indian", "effort": 1, "tags": ["Light"]},
    {"name": "Sambar Rice", "meal": "Lunch", "cuisine": "South Indian", "effort": 2, "tags": ["Light"]},
    {"name": "Lemon Rice", "meal": "Lunch", "cuisine": "South Indian", "effort": 1, "tags": ["Light"]},
    {"name": "Veg Biryani", "meal": "Lunch", "cuisine": "Mix", "effort": 4, "tags": ["Heavy", "Comfort"]},
    {"name": "Aloo Gobi + Roti", "meal": "Lunch", "cuisine": "North Indian", "effort": 2, "tags": ["Light"]},
    {"name": "Bhindi Masala + Roti", "meal": "Lunch", "cuisine": "North Indian", "effort": 2, "tags": ["Light"]},
    {"name": "Baingan Bharta + Roti", "meal": "Lunch", "cuisine": "North Indian", "effort": 3, "tags": ["Comfort"]},
    {"name": "Mix Veg + Roti", "meal": "Lunch", "cuisine": "North Indian", "effort": 2, "tags": ["Light"]},
    {"name": "Palak Paneer + Roti", "meal": "Lunch", "cuisine": "North Indian", "effort": 3, "tags": ["Comfort"]},
    {"name": "Paneer Bhurji + Roti", "meal": "Lunch", "cuisine": "North Indian", "effort": 2, "tags": ["Quick"]},
    {"name": "Lauki Sabzi + Roti", "meal": "Lunch", "cuisine": "North Indian", "effort": 2, "tags": ["Light"]},
    {"name": "Aloo Methi + Roti", "meal": "Lunch", "cuisine": "North Indian", "effort": 2, "tags": ["Healthy", "Light"]},
    {"name": "Patta Gobi Matar + Roti", "meal": "Lunch", "cuisine": "North Indian", "effort": 2, "tags": ["Light"]},
    {"name": "Turai ki Sabzi + Roti", "meal": "Lunch", "cuisine": "North Indian", "effort": 2, "tags": ["Light", "Healthy"]},
    {"name": "Gawar Fali + Roti", "meal": "Lunch", "cuisine": "North Indian", "effort": 2, "tags": ["Light"]},
    {"name": "Chawli (Black-eyed peas) + Rice", "meal": "Lunch", "cuisine": "Mix", "effort": 2, "tags": ["Comfort"]},

    # -------- DINNER --------
    {"name": "Khichdi", "meal": "Dinner", "cuisine": "Mix", "effort": 1, "tags": ["Light"]},
    {"name": "Roti Sabzi", "meal": "Dinner", "cuisine": "North Indian", "effort": 2, "tags": ["Light"]},
    {"name": "Paneer Bhurji", "meal": "Dinner", "cuisine": "North Indian", "effort": 2, "tags": ["Quick"]},
    {"name": "Palak Paneer", "meal": "Dinner", "cuisine": "North Indian", "effort": 3, "tags": ["Comfort"]},
    {"name": "Veg Daliya", "meal": "Dinner", "cuisine": "Mix", "effort": 1, "tags": ["Light"]},
    {"name": "Dal Khichdi", "meal": "Dinner", "cuisine": "Mix", "effort": 1, "tags": ["Light"]},
    {"name": "Vegetable Soup", "meal": "Dinner", "cuisine": "Mix", "effort": 1, "tags": ["Light"]},
    {"name": "Tomato Soup + Toast", "meal": "Dinner", "cuisine": "Mix", "effort": 1, "tags": ["Light"]},
    {"name": "Moong Dal + Roti", "meal": "Dinner", "cuisine": "North Indian", "effort": 1, "tags": ["Light"]},
    {"name": "Tinda Sabzi + Roti", "meal": "Dinner", "cuisine": "North Indian", "effort": 2, "tags": ["Light"]},
    {"name": "Karela Sabzi + Roti", "meal": "Dinner", "cuisine": "North Indian", "effort": 2, "tags": ["Light"]},
    {"name": "Capsicum Paneer + Roti", "meal": "Dinner", "cuisine": "North Indian", "effort": 3, "tags": ["Comfort"]},
    {"name": "Stuffed Paratha", "meal": "Dinner", "cuisine": "North Indian", "effort": 4, "tags": ["Heavy"]},
    {"name": "Veg Fried Rice", "meal": "Dinner", "cuisine": "Mix", "effort": 2, "tags": ["Quick"]},
    {"name": "Hakka Noodles", "meal": "Dinner", "cuisine": "Mix", "effort": 2, "tags": ["Quick"]},
    {"name": "Paneer Tikka (home)", "meal": "Dinner", "cuisine": "North Indian", "effort": 3, "tags": ["Comfort"]},
    {"name": "Masoor Dal + Rice", "meal": "Dinner", "cuisine": "North Indian", "effort": 2, "tags": ["Light", "Comfort"]},
    {"name": "Aloo Shimla Mirch + Roti", "meal": "Dinner", "cuisine": "North Indian", "effort": 2, "tags": ["Light"]},
    {"name": "Moong Sprouts Sabzi + Roti", "meal": "Dinner", "cuisine": "Mix", "effort": 2, "tags": ["Light", "Healthy"]},
    {"name": "Aloo Baingan + Roti", "meal": "Dinner", "cuisine": "North Indian", "effort": 2, "tags": ["Comfort"]},
]

def create_page(dish):
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Dish Name": {
                "title": [{"text": {"content": dish["name"]}}]
            },
            "Meal Type": {
                "select": {"name": dish["meal"]}
            },
            "Cuisine": {
                "select": {"name": dish["cuisine"]}
            },
            "Effort": {
                "number": dish["effort"]
            },
            "Tags": {
                "multi_select": [{"name": tag} for tag in dish["tags"]]
            }
        }
    }

    response = requests.post(url, headers=headers, json=data)
    return response.status_code, response.json()

for dish in dishes:
    status, res = create_page(dish)
    print(status, dish["name"])