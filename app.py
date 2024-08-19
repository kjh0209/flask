from flask import Flask, request, jsonify, render_template
import requests
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('/index.html')

API_KEY = "0e29646040154781950fab3b908ae536" # 능동적으로 바꿀 것
SD_SCHUL_CODE = "8321124"  # 행정표준코드
ATPT_OFCDC_SC_CODE = "P10" # 시도교육청코드

def get_menu(when): # 오늘 급식
    BASE_URL = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    today = datetime.now().strftime('%Y%m%d')
    params = {
        "KEY": API_KEY,
        "Type": "json",
        "ATPT_OFCDC_SC_CODE": ATPT_OFCDC_SC_CODE,
        "SD_SCHUL_CODE": SD_SCHUL_CODE,

        "MLSV_YMD": today,
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()
    if(when == "전체"): # 조식, 중식, 석식을 함께
        # return data["mealServiceDietInfo"][1]["row"]
        # return len(data["mealServiceDietInfo"][1]["row"])
        # return data["mealServiceDietInfo"][1]["row"][0]
        # return data["mealServiceDietInfo"][1]["row"][0]["MMEAL_SC_NM"]
        try:
            menu = ""
            search = data["mealServiceDietInfo"][1]["row"]
            for i in range(0, len(search), 1):
                jjs = search[i]["MMEAL_SC_NM"]
                if jjs == "조식" or jjs == "중식" or jjs == "석식":
                    menu = menu +"<"+ jjs +">\n"+ search[i]["DDISH_NM"].replace("<br/>", "\n\n")
            return menu
                
        except (KeyError, IndexError):
            return "오늘 메뉴를 불러오는데 실패했습니다."

    else: # 조식 or 중식 or 석식만
        try:
            for meal in data["mealServiceDietInfo"][1]["row"]:
                if meal["MMEAL_SC_NM"] == when:
                    menu = meal["DDISH_NM"].replace("<br/>", "\n")
                    return menu
            
            return "오늘 메뉴를 불러오는데 실패했습니다."
        except (KeyError, IndexError):
            return "오늘 메뉴를 불러오는데 실패했습니다."
        
def get_timetable():
    BASE_URL = "https://open.neis.go.kr/hub/hisTimetable"
    # https://open.neis.go.kr/hub/hisTimetable?ATPT_OFCDC_SC_CODE=P10&SD_SCHUL_CODE=8321124&AY=2024&SEM=1&ALL_TI_YMD=20240509
    today = datetime.now().strftime('%Y%m%d')
    params = {
        "KEY": API_KEY,
        "Type": "json",
        "ATPT_OFCDC_SC_CODE": ATPT_OFCDC_SC_CODE,
        "SD_SCHUL_CODE": SD_SCHUL_CODE,

        "ALL_TI_YMD": today,
        # "GRADE": 학년
        # "ITRT_CNTNT": 과목명
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    search = data["hisTimetable"][1]["row"]
    timetable = "\n"
    grade = 0
    try:
        for i in range(0, len(search), 1):
            if grade != search[i]["GRADE"]:
                grade += 1
                timetable += "<"+str(grade)+"학년 시간표>\n"
            timetable += search[i]["ITRT_CNTNT"] + "\n"
        return timetable
    except:
        return "시간표를 불러오는데 실패했습니다."

@app.route('/menu/breakfast', methods=['GET', 'POST']) # 급식
def menu_breakfast():
    response_text = get_menu("조식")
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

@app.route('/menu/lunch', methods=['GET', 'POST']) # 급식
def menu_lunch():
    response_text = get_menu("중식")
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

@app.route('/menu/dinner', methods=['GET', 'POST']) # 급식
def menu_dinner():
    response_text = get_menu("석식")
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

@app.route('/menu/all', methods=['GET', 'POST']) # 급식
def menu_all():
    response_text = get_menu("전체")
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

@app.route('/hello', methods=['GET', 'POST']) # 인사
def hello():
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

@app.route('/timetable', methods=['GET', 'POST']) # 시간표
def timetable():
    response_text = get_timetable()
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

@app.route('/developers', methods=['GET', 'POST']) # 각인
def developers():
    response_text = "33기 김윤석, 33기 김지혁"
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
