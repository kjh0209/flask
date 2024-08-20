from flask import Flask, request, jsonify, render_template
import requests
from datetime import timedelta
import datetime
import re

app = Flask(__name__)

def convert_date_format(date_str):
    # 한글과 공백 제거
    date_str = re.sub(r'[^\d]', ' ', date_str).strip()

    # 년, 월, 일을 추출
    month, day = date_str.split() #월, 일만 들어와도 20240809 이런 식으로 변환 가능하게 만들기
    year = 2024
    # 'YYYYMMDD' 형식으로 변환
    formatted_date = f"{year}{month.zfill(2)}{day.zfill(2)}"
    
    return formatted_date


def datecal(today):
    if not today:
        return "날짜가 제대로 입력되지 않았습니다."
    else:
        if today == '오늘':
            today = datetime.date.today()
            today = str(today)
            today = today.split('-')
            today = ''.join(today)
        elif today == '내일':
            today = datetime.date.today()
            today = today + timedelta(days=1)
            today = str(today)
            today = today.split('-')
            today = ''.join(today)
        elif today == '어제':
            today = datetime.date.today()
            today = today - timedelta(days=1)
            today = str(today)
            today = today.split('-')
            today = ''.join(today)
        else:
            today = convert_date_format(today)
    return int(today)

def convert_class_format(class_str):
    # 숫자만 추출하는 정규식 패턴
    pattern = r'(\d)[^\d]*(\d)'
    
    # 정규식으로 학년과 반 추출
    match = re.search(pattern, class_str)
    
    if match:
        grade = match.group(1)
        classroom = match.group(2)
        return f"{grade},{classroom}"
    else:
        return "Invalid format"

def ex_res_data(response_text):
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
    return response_data

@app.route("/")
def index():
    return render_template('/index.html')

API_KEY = "0e29646040154781950fab3b908ae536" # 능동적으로 바꿀 것
SD_SCHUL_CODE = "8321124"  # 행정표준코드
ATPT_OFCDC_SC_CODE = "P10" # 시도교육청코드

def get_menu(when): # 오늘 급식
    BASE_URL = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    today = request.json.get('action').get('detailParams').get('날짜').get('origin')
    #today = 20240509 # [중요] 배포시 삭제할 것
    today = datecal(today)
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
                    menu = menu +"\n\n<"+ jjs +">\n"+ search[i]["DDISH_NM"].replace("<br/>", "\n")
            today = str(today)
            return today[:4]+'년 '+today[4:6]+'월 '+today[6:]+'일\n '+menu
                
        except (KeyError, IndexError):
            today = str(today)
            return today[:4]+'년 '+today[4:6]+'월 '+today[6:]+'일 '+"메뉴를 불러오는데 실패했습니다."

    else: # 조식 or 중식 or 석식만
        try:
            for meal in data["mealServiceDietInfo"][1]["row"]:
                if meal["MMEAL_SC_NM"] == when:
                    menu = "<"+when+">\n"+meal["DDISH_NM"].replace("<br/>", "\n")
                    today = str(today)
                    return today[:4]+'년 '+today[4:6]+'월 '+today[6:]+'일\n '+menu
            today = str(today)
            return today[:4]+'년 '+today[4:6]+'월 '+today[6:]+'일 '+"메뉴를 불러오는데 실패했습니다."
        except (KeyError, IndexError):
            today = str(today)
            return today[:4]+'년 '+today[4:6]+'월 '+today[6:]+'일 '+"메뉴를 불러오는데 실패했습니다."
        
def get_timetable():
    BASE_URL = "https://open.neis.go.kr/hub/hisTimetable"
    # https://open.neis.go.kr/hub/hisTimetable?ATPT_OFCDC_SC_CODE=P10&SD_SCHUL_CODE=8321124&AY=2024&SEM=1&ALL_TI_YMD=20240509
    today = request.json.get('action').get('detailParams').get('날짜').get('origin')
    grade = request.json.get('action').get('detailParams').get('학년반').get('origin')
    grade = convert_class_format(grade)
    grade = str(grade)
    #today = 20240509 # [중요] 배포시 삭제할 것
    today = datecal(today) #시간표 몇학년 몇반 입력해서 볼 수 있게 하기
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
    try:
        search = data["hisTimetable"][1]["row"]
        # return str(search[len(search)-1]["CLASS_NM"])
        # return search
        timetable = "\n"
        GRADE = 0
        CLASS_NM = 0
        if grade == 'all':
          for i in range(0, len(search), 1):
            if str(GRADE) != search[i]["GRADE"]:
                GRADE += 1
                CLASS_NM = 0
                timetable += "\n<"+str(GRADE)+"학년 시간표>\n"
            if (str(CLASS_NM) != search[i]["CLASS_NM"] and str(search[i]["CLASS_NM"]) != "None"):
                CLASS_NM += 1
                timetable += "<"+str(CLASS_NM)+"반>\n"

            timetable += search[i]["ITRT_CNTNT"] + "\n"
        else:
            GRADE = int(grade.split(',')[0])
            CLASS_NM = int(grade.split(',')[1])
            timetable += "<"+str(GRADE)+"학년 시간표>\n"
            timetable += "<"+str(CLASS_NM)+"반>\n"
            for i in range(0, len(search), 1): 
                if str(GRADE) == search[i]["GRADE"]: 
                  if (str(CLASS_NM) == search[i]["CLASS_NM"] and str(search[i]["CLASS_NM"]) != "None"):
                    timetable += search[i]["ITRT_CNTNT"] + "\n"
                elif str(GRADE) < search[i]["GRADE"]:
                    break
        today = str(today)
        return today[:4]+'년 '+today[4:6]+'월 '+today[6:]+'일\n '+timetable
    except:
        today = str(today)
        return today[:4]+'년 '+today[4:6]+'월 '+today[6:]+'일 '+"시간표를 불러오는데 실패했습니다."
    
def get_statement():
    today = request.json.get('action').get('detailParams').get('날짜').get('origin')
    #today = 20240509 # [중요] 배포시 삭제할 것
    today = datecal(today)
    statement = ["급식: 정상", "시간표: 정상", today] # 급식, 시간표

    BASE_URL = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    params = {
        "KEY": API_KEY,
        "Type": "json",
        "ATPT_OFCDC_SC_CODE": ATPT_OFCDC_SC_CODE,
        "SD_SCHUL_CODE": SD_SCHUL_CODE,

        "MLSV_YMD": today,
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    try:
        search = data["mealServiceDietInfo"][1]["row"]
    except:
        statement[0] = "급식: 오류"

    BASE_URL = "https://open.neis.go.kr/hub/hisTimetable"
    params = {
        "KEY": API_KEY,
        "Type": "json",
        "ATPT_OFCDC_SC_CODE": ATPT_OFCDC_SC_CODE,
        "SD_SCHUL_CODE": SD_SCHUL_CODE,

        "ALL_TI_YMD": today,
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    try:
        search = data["hisTimetable"][1]["row"]
    except:
        statement[1] = "시간표: 오류"
    return [i for i in statement]

def get_calendar():
    BASE_URL = "https://open.neis.go.kr/hub/SchoolSchedule"
    today = request.json.get('action').get('detailParams').get('월').get('origin')
    if today=="이번달" or "이번 달":
        today = datetime.date.today()
        this_month_first = int(str(today.year) + str(today.month).zfill(2) + '01') # 20240801
        month = str(today.month)+'월'
    elif today=="저번달" or "저번 달":
        today = datetime.date.today()
        this_month_first = int(str(today.year) + str(int(str(today.month))-1).zfill(2) + '01') # 20240801
        month = str(int(str(today.month))-1)+'월'
    elif today=="다음달" or "다음 달":
        today = datetime.date.today()
        this_month_first = int(str(today.year) + str(int(str(today.month))+1).zfill(2) + '01') # 20240801
        month = str(int(str(today.month))+1)+'월'
    else:
        this_month_first = int("2024"+today.replace("월", "").zfill(2)+'01')
        month = today
    params = {
        "KEY": API_KEY,
        "Type": "json",
        "ATPT_OFCDC_SC_CODE": ATPT_OFCDC_SC_CODE,
        "SD_SCHUL_CODE": SD_SCHUL_CODE,

        "AA_FROM_YMD": this_month_first,
        "AA_TO_YMD": this_month_first+30,
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    try:
        search = data["SchoolSchedule"][1]["row"]
        calendar = "<"+month+" 학사일정>\n"
        for i in range(0, len(search), 1):
            calendar += search[i]["AA_YMD"] + ": " + search[i]["EVENT_NM"] + "\n"
        return calendar
    except:
        return month + " 학사일정을 불러오는 데에 실패했습니다."


@app.route('/menu/breakfast', methods=['GET', 'POST']) # 급식
def menu_breakfast():
    response_text = get_menu("조식")
    return jsonify(ex_res_data(response_text))

@app.route('/menu/lunch', methods=['GET', 'POST']) # 급식
def menu_lunch():
    response_text = get_menu("중식")
    return jsonify(ex_res_data(response_text))

@app.route('/menu/dinner', methods=['GET', 'POST']) # 급식
def menu_dinner():
    response_text = get_menu("석식")
    return jsonify(ex_res_data(response_text))

@app.route('/menu/all', methods=['GET', 'POST']) # 급식
def menu_all():
    response_text = get_menu("전체")
    return jsonify(ex_res_data(response_text))

@app.route('/hello', methods=['GET', 'POST']) # 인사
def hello():
    response_text = "안녕하세요, 현재 datetime은", datetime.now().strftime("%Y%m%d")
    return jsonify(ex_res_data(response_text))

@app.route('/timetable', methods=['GET', 'POST']) # 시간표
def timetable():
    response_text = get_timetable()
    return jsonify(ex_res_data(response_text))

@app.route('/developers', methods=['GET', 'POST']) # 각인
def developers():
    response_text = "33기 김윤석, 33기 김지혁"
    return jsonify(ex_res_data(response_text))

@app.route('/help', methods=['GET', 'POST']) # 각인
def help():
    response_text = """
    /메뉴, /급식, /밥: 조식, 중식, 석식 출력\n
    /조식, /아침, /아침밥: 조식 출력\n
    /중식, /점심, /점심밥: 중식 출력\n
    /석식, /저녁, /저녁밥: 석식 출력\n
    /시간표, /수업, /과목: 오늘의 시간표 출력\n
    /도움말, /도움, /help: 도움말 출력\n
    /농담, /넝담, /장난: 봇과의 일상적인 대화\n
    /개발자: 우리를 누가 만들었는지 확인해보세요\n
    \n
    급식 메뉴나 시간표 등 정보를 불러오는데 실패하는 경우 NEIS에 정보가 없는지 확인하세요.\n
    어제, 오늘, 또는 내일과 같은 말을 함께 전달하면 챗봇이 이를 파악할 수 있습니다.\n
    ex: 내일 급식이 뭐야?
    """
    return jsonify(ex_res_data(response_text))

@app.route('/state', methods=['GET', 'POST']) # 봇상태
def state():
    response_text = get_statement()
    return jsonify(ex_res_data(response_text))

@app.route('/calendar', methods=['GET', 'POST']) # 학사일정
def calendar():
    response_text = get_calendar()
    return jsonify(ex_res_data(response_text))
