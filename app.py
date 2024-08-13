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
SCHOOL_CODE = "8321124"  # Jeonbuk Science High School code
SCHOOL_REGION = "P10"
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
    try:
        # Find the lunch menu by checking the MMEAL_SC_NM field for "중식"
        for meal in data["mealServiceDietInfo"][1]["row"]:
            if meal["MMEAL_SC_NM"] == "중식":  # "중식" means lunch
                menu = meal["DDISH_NM"].replace("<br/>", "\n")
                return menu
        
        return "No lunch menu available for today."
    except (KeyError, IndexError):
        # Return a default message if the expected data isn't found
        return "No lunch menu available for today."


@app.route('/message', methods=['POST'])
def message():
    # Always fetch the lunch menu
    response_text = get_lunch_menu()

    # Construct the response to be sent back to KakaoTalk
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
