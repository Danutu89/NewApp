from app import app,db
import geoip2.database
from datetime import datetime
import httpagentparser
import hashlib
from datetime import datetime
from flask import request, session
from models import Analyze_Pages, Analyze_Session, Ip_Coordinates
import requests
from flask_login import current_user
from urllib.parse import urlparse

gip = geoip2.database.Reader('GeoLite2-City.mmdb')

userOS = None
userIP = None
userCity = None
userBrowser = None
userCountry = None
userContinent = None
userLanguage = None
sessionID = None
bot = False
iso_code = None

def create_pages(data):
    query = Analyze_Pages(
        None,
        data[0],
        data[1],
        data[2],
        None
    )
    db.session.add(query)
    db.session.commit()

def update_pages(pageId):
    query = db.session.query(Analyze_Pages).filter_by(id=pageId).first_or_404()
    query.visits = query.visits + 1
    db.session.commit()

def update_or_create_page(data):
    query = db.session.query(Analyze_Pages).filter_by(name=data[0],session=data[1]).first()
    
    if query is None:
        create_pages(data)
    else:
        update_pages(query.id)

def create_session(data):
    query = Analyze_Session(
        None,
        data[0],
        data[1],
        data[2],
        data[3],
        data[4],
        data[5],
        data[6],
        data[7],
        data[8],
        data[9],
        data[10],
        data[11]
    )
    db.session.add(query)
    db.session.commit()

def parseVisitator(data):
    update_or_create_page(data)

def getSession():
    global sessionID
    time = datetime.now().replace(microsecond=0)
    if 'user' not in session:
        if current_user.is_authenticated:
            lines = (str(current_user.id)+current_user.name).encode('utf-8')
        else:
            lines = (str(time)+userIP).encode('utf-8')
        session['user'] = hashlib.md5(lines).hexdigest()
        sessionID = session['user']
        try:
            if request.headers['referer'] != 'android-app://nl.newapp.app':
                temp = urlparse(str(request.headers['referer']))
                if len(temp.netloc.split(".")) > 2:
                    domain = temp.netloc.split(".")[1]
                else:
                    domain = temp.netloc.split(".")[0]
                referer = str(domain)[0].upper() + str(domain)[1:]
                if referer == 'Google' or referer == 'Bing' or referer == 'Yandex' or referer == 'Duckduckgo':
                    referer = 'Organic'
                if referer == 'nl' or referer == 'Newapp':
                    referer = None
            else:
                referer = 'App'
        except:
            referer = 'Direct'
    
        data = [userIP, userContinent, userCountry, userCity, userOS, userBrowser, sessionID, time, bot, str(userLanguage).lower(),referer,iso_code]
        create_session(data)
    else:
        sessionID = session['user']

def getAnalyticsData():
    if request.endpoint != 'static' and request.endpoint != 'sitemap' and request.endpoint != 'opensearch' and request.endpoint != 'flask_session':
        global userOS, userBrowser, userIP, userContinent, userCity, userCountry, sessionID, bot, userLanguage, iso_code
        userInfo = httpagentparser.detect(request.headers.get('User-Agent'))
        try:
            userOS = userInfo['platform']['name']
            userBrowser = userInfo['browser']['name']
            bot = userInfo['bot']
        except:
            pass
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            userIP = request.environ['REMOTE_ADDR']
        else:
            userIP = request.environ['HTTP_X_FORWARDED_FOR']

        if userIP != '127.0.0.1':
            local_ip = db.session.query(Ip_Coordinates).filter_by(ip=userIP).first()

            if local_ip is None:
                try:
                    res = gip.city(userIP)
                except:
                    ip = userIP.split(', ')
                    res = gip.city(ip[0])
                try:                                                                                                 
                    userCountry = res.country.name
                    userContinent = res.continent.name
                    userCity = res.city.name
                    iso_code = res.country.iso_code
                    try:
                        api_2 = requests.get(("https://restcountries.eu/rest/v2/alpha/{}").format(res.country.iso_code))
                        result_2 = api_2.json()
                        userLanguage = result_2['languages'][0]['iso639_1']
                    except Exception as e:
                        print("Not supported country", res.country.name)
                        print(e)
                except Exception as e:
                    print("Could not find: ", userIP)
                    print(e)
            else:
                api_2 = requests.get(
                    ("https://restcountries.eu/rest/v2/alpha/{}").format(local_ip.location.iso_code))
                result_2 = api_2.json()
                userCountry = result_2['name']
                userContinent = local_ip.location.continent
                userCity = local_ip.location.city
                iso_code = str(local_ip.location.iso_code).upper()
                userLanguage = result_2['languages'][0]['iso639_1']

            getSession()
    

def GetSessionId():
    return sessionID
