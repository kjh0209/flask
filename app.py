from flask import Flask, request, jsonify, render_template
import requests
from datetime import datetime
app = Flask(__name__)

@app.route("/")
def index():
    return render_template('./index.html')

# Neis API credentials
API_KEY = "0e29646040154781950fab3b908ae536"
BASE_URL = "https://open.neis.go.kr/hub/mealServiceDietInfo"
SCHOOL_CODE = "P100000292"  # Jeonbuk Science High School code
SCHOOL_REGION = "Q10"  # Code for Jeollabuk-do region

def get_lunch_menu():
    today = datetime.now().strftime('%Y%m%d')
    params = {
        "KEY": API_KEY,
        "Type": "json",
        "ATPT_OFCDC_SC_CODE": SCHOOL_REGION,
        "SD_SCHUL_CODE": SCHOOL_CODE,
        "MLSV_YMD": today
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if "mealServiceDietInfo" in data:
        meal_info = data["mealServiceDietInfo"][1]["row"][0]["DDISH_NM"]
        menu = meal_info.replace("<br/>", "\n")  # Replace HTML line breaks with newlines
        return menu
    else:
        return "No lunch menu available for today."

@app.route('/message', methods=['POST'])
def message():
    user_message = request.json.get('userRequest').get('utterance')
    response_text = ""

    if "lunch" in user_message.lower():
        response_text = get_lunch_menu()
    else:
        response_text = "Sorry, I can only provide lunch menus."

    response_data = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": response_text
                    }
                }
            ]
        }
    }

    return jsonify(response_data)
