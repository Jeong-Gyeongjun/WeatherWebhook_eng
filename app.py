#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import re

import pytz
from datetime import datetime, timedelta

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

from flask import Flask
from flask import request
from flask import make_response


app = Flask(__name__)


INTENT_NAME = 'weather'
PARAMETERS_CLASS = ['address', 'date-time', 'unit']

DEFAULT_CITY = 'Daejeon'
TIMEZONE = 'Asia/Seoul'

def get_strings(req, strs) :

    for i in strs :
        if (req == None):
            return None
        req = req.get(i)
    return req



@app.route('/webhook', methods=['POST'])
def webhook():    
    req = request.get_json(silent=True, force=True)
    
    city = DEFAULT_CITY
    cityRequested = get_strings(req, ['result', 'parameters', PARAMETERS_CLASS[0]])
    
    if (cityRequested != None):
        if ('{\"city\"' in cityRequested and '\"}' in cityRequested):
            city = cityRequested[7:-2]

    date = get_strings(req, ['result', 'parameters', PARAMETERS_CLASS[1]])
    unit = get_strings(req, ['result', 'parameters', PARAMETERS_CLASS[2]])

    #print(city, date, unit)
    data = makeWebhookResult(req, city, date, unit)

    print(data)
    return data


def makeWebhookResult(req, city, date, unit):
    if (get_strings(req, ['result', 'metadata', 'intentName']) != INTENT_NAME):
        return {}
    baseurl = 'http://query.yahooapis.com/v1/public/yql?q=%20select%20*%20from%20weather.forecast%20where%20woeid%20in%20(select%20woeid%20from%20geo.places(1)%20where%20text=%27' + city + '%27)&format=json'
    result = urlopen(baseurl).read().decode('utf-8')
    
    data = json.loads(result).get('query')

    if(data.get('results') == None):
        #API Server error
        sentence = 'server error'
        return {
            'speech': sentence,
            'displayText': sentence,
            'source': 'apiai-yahoo-weather'
        }

    deltaDate = 0

    r = re.compile('\d\d\d\d-\d\d-\d\d')

    if(r.match(date[0:10]) is not None) :
        querytime = datetime.strptime(get_strings(data,['created']), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc).astimezone(pytz.timezone(TIMEZONE)).replace(tzinfo=None)
        requestedtime = datetime.strptime(date[0:10], '%Y-%m-%d')
    
        delta = requestedtime - querytime
        deltaDate = delta.days + 1


    if(deltaDate < 0):
        sentence = 'I don\'t want to find the past weather...' 
        return {
            'speech': sentence,
            'displayText': sentence,
            'source': 'apiai-yahoo-weather'
        }

    if(deltaDate > 9):
        sentence = 'I can find weather only within 10 days...'
        return {
            'speech': sentence,
            'displayText': sentence,
            'source': 'apiai-yahoo-weather'
        }


    weather = get_strings(data, ['results','channel','item','forecast'])[deltaDate]

    #print(json.dumps(data, indent=4))
    #print(json.dumps(weather, indent=4))
    #print(deltaDate)
    
    sentence =  ('It will be ' 
    + weather.get('text') 
    + ' at ' 
    + weather.get('date') 
    + ', in ' 
    + city 
    + '. Minimum temperature near ' 
    + str(int(FConversion(int(weather.get('low')), unit))) 
    + ' degrees ' 
    + '. Maximum temperature near ' 
    + str(int(FConversion(int(weather.get('high')), unit)))  
    + ' degrees')

    return {
        'speech': sentence,
        'displayText': sentence,
        'source': 'apiai-yahoo-weather'
    }

def FConversion(num, unit):
    if(unit == 'C') :
        return (num - 32)/1.8
    if(unit == 'K') :
        return (num + 459.67)/1.8
    if(unit == 'R') :
        return num + 459.67
    else :
        return num



if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, port=port, host='0.0.0.0')



