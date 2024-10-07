import requests, json, apprise
from decouple import config
from datetime import datetime

WEATHERAPI_KEY = config('WEATHERAPI_KEY')
WEATHERAPI_ZIP = config('WEATHERAPI_ZIP')

def api_data():

    headers = {
    "Content-Type": "application/json",
    }
    
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHERAPI_KEY}&q={WEATHERAPI_ZIP}&days=1&aqi=no&alerts=no"

    payload = {}
    response = requests.post(url, json=payload, headers=headers)

    results = response.json()

    # with open('db.json', 'w', encoding='utf8') as f:
    #    json.dump(results, f, ensure_ascii=False, indent=4)
        
    return results

def send_msg(title, msg):

    apobj = apprise.Apprise()
    hooks = list(config('WEATHERAPI_WEB_HOOKS').split(','))
    for i in hooks:
        apobj.add(i)
    
    apobj.notify(
        body=msg,
        title=title,
    )

if __name__ == "__main__":
    data = api_data()
    now = datetime.now()

    try:
        city = data['location']['name']
        state = data['location']['region']
        cTemp = data['current']['temp_f']
        cCondition = data['current']['condition']['text']
        cWindDir = data['current']['wind_dir']
        cWindSpeed = data['current']['wind_mph']

        # forecast
        forecast = data['forecast']['forecastday'][0]['day']
        fTempMax = forecast['maxtemp_f']
        fTempMin = forecast['mintemp_f']
        fRainChance = forecast['daily_chance_of_rain']
        fSnowChance = forecast['daily_chance_of_snow']
        fCondition = forecast['condition']['text']
    except:
        title = 'Error'
        msg = 'Failed to parse JSON from API'
        send_msg(title, msg)
    else:
        title = f'### Weather for {city}, {state}'
        msg = f'''
        Currently "**{cCondition}**", forecast "**{fCondition}**"
        Wind; Current: {cWindDir} at {cWindSpeed} mph
        Temp; Current: **{cTemp}** F, Min **{fTempMin}** F, Max **{fTempMax}** F
        {fRainChance}% Chance of Rain
        {fSnowChance}% Chance of Snow
        '''
        
        send_msg(title, msg)