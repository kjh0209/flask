from flask import Flask, request, jsonify, render_template
import requests
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('./index.html')

API_KEY = "0e29646040154781950fab3b908ae536"
BASE_URL = "https://open.neis.go.kr/hub/mealServiceDietInfo"
SD_SCHUL_CODE = "8321124"  # 행정표준코드
ATPT_OFCDC_SC_CODE = "P10" # 시도교육청코드

def get_lunch_menu(): # 오늘 급식
    today = datetime.now().strftime('%Y%m%d')
    params = {
        "KEY": API_KEY,
        "Type": "json",
        "ATPT_OFCDC_SC_CODE": ATPT_OFCDC_SC_CODE,
        "SD_SCHUL_CODE": SD_SCHUL_CODE,
        "MLSV_YMD": today
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()
    try:
        for meal in data["mealServiceDietInfo"][1]["row"]:
            if meal["MMEAL_SC_NM"] == "조식":
                menu = meal["DDISH_NM"].replace("<br/>", "\n")
                return menu
            elif meal["MMEAL_SC_NM"] == "중식":
                menu = meal["DDISH_NM"].replace("<br/>", "\n")
                return menu
            elif meal["MMEAL_SC_NM"] == "석식":
                menu = meal["DDISH_NM"].replace("<br/>", "\n")
                return menu
        
        return "메뉴를 불러오는데 실패했습니다."
    except (KeyError, IndexError):
        return "메뉴를 불러오는데 실패했습니다."


@app.route('/menu', methods=['POST']) # 급식
def message():
    response_text = get_lunch_menu()
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

@app.route('/hello', methods=['GET']) # 인사
def message():
    response_text = "안녕하세요, 현재 datetime은", datetime.now().strftime("%Y%m%d")
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
