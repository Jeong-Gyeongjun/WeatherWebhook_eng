#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

import json
import os

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

from flask import Flask
from flask import request
from flask import make_response



INTENT_NAME = '날씨질문'
CITY_NAME = "Daejeon"
DATE_ARRAY = ['오늘','내일','글피']
YAHOO_WEATHERCODE = {
0 :  '토네이도가 불겠습니다',
1 :  '열대성 태풍이 있겠습니다',
2 :  '허리케인이 불겠습니다',
3 :  '맹렬한 뇌우가 있겠습니다',
4 :  '뇌우가 있겠습니다',
5 :  '눈과 비가 섞어 내리겠습니다',
6 :  '비와 진눈깨비가 섞어 내리겠습니다',
7 :  '눈과 진눈깨비가 섞어 내리겠습니다',
8 :  '결빙성 진눈깨비가 섞어 내리겠습니다',
9 :  '진눈깨비가 내리겠습니다',
10:  '어는 비가 내리겠습니다',
11:  '소나기가 있겠습니다',
12:  '소나기가 있겠습니다',
13:  '소낙눈이 내리겠습니다',
14:  '눈이 약간 내리겠습니다',
15:  '날린눈이 내리겠습니다',
16:  '눈이 내리겠습니다',
17:  '싸락눈이 내리겠습니다',
18:  '진눈깨비가 내리겠습니다',
19:  '미세먼지가 많겠습니다',
20:  '안개가 끼겠습니다',
21:  '실안개가 끼겠습니다',
22:  '짙은안개가 끼겠습니다',
23:  '강한 바람이 불겠습니다',
24:  '바람이 불겠습니다',
25:  '춥겠습니다',
26:  '구름이 끼겠습니다',
27:  '구름이 많겠습니다',
28:  '구름이 많겠습니다',
29:  '구름이 조금 끼겠습니다',
30:  '구름이 조금 끼겠습니다',
31:  '맑겠습니다',
32:  '화창하겠습니다',
33:  '하늘이 맑겠습니다',
34:  '하늘이 맑겠습니다',
35:  '비와 싸락눈이 섞어 내리겠습니다',
36:  '덥겠습니다',
37:  '국지성 뇌우가 있겠습니다',
38:  '산발적인 뇌우가 있겠습니다',
39:  '산발적인 뇌우가 있겠습니다',
40:  '산발적 소나기가 내리겠습니다',
41:  '폭설이 내리겠습니다',
42:  '산발적 눈과 비가 내리겠습니다',
43:  '폭설이 내리겠습니다',
44:  '부분적으로 구름이 끼겠습니다',
45:  '뇌우가 있겠습니다',
46:  '소낙눈이 내리겠습니다',
47:  '국지성 소낙눈이 내리겠습니다'}

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    print('get data from request...')
    data = request.get_json(silent=True, force=True)
    #print(json.dumps(data, indent=4))

    print('get weather from Yahoo...')

    req = makeWebhookResult(data)
    req = json.dumps(req, indent=4)

    print('make the response...')

    result = make_response(req)
    result.headers['Content-Type'] = 'application/json'
    return result



def makeWebhookResult(req):
    if req.get("result").get("action").decode('ascii').encode('utf-8') != INTENT_NAME:
        return {}
    baseurl = 'http://query.yahooapis.com/v1/public/yql?q=%20select%20*%20from%20weather.forecast%20where%20woeid%20in%20(select%20woeid%20from%20geo.places(1)%20where%20text=%27' + CITY_NAME + '%27)&format=json'
    result = urlopen(baseurl).read().decode('utf-8')
    data = json.loads(result)

    date = 0
    if(req.get('result').get('parameters').get('date').decode('ascii').encode('utf-8') == DATE_ARRAY[0]) :
        date = 0
    if(req.get('result').get('parameters').get('date').decode('ascii').encode('utf-8') == DATE_ARRAY[1]) :
        date = 1
    if(req.get('result').get('parameters').get('date').decode('ascii').encode('utf-8') == DATE_ARRAY[2]) :
        date = 2

    data = data.get('query').get('results').get('channel').get('item').get('forecast')[date]

    sentence = req.get('result').get('parameters').get('date')+' 날씨는 최저 ' + str(int(FtoC(int(data.get('low'))))) + '도 최고 ' + str(int(FtoC(int(data.get('high'))))) + '도로 '+ YAHOO_WEATHERCODE[int(data.get('code'))]


    return {
        'speech': sentence,
        'displayText': sentence,
        'source': 'apiai-yahoo-weather'
    }

def FtoC(num):
    return (num-32)/1.8


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, port=port, host='0.0.0.0')
