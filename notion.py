import requests, json, apprise
from decouple import config
from datetime import datetime

NOTION_KEY = config('NOTION_KEY')
NOTION_DATABASE_ID = config('NOTION_DATABASE_ID')


headers = {
    "Authorization": "Bearer " + NOTION_KEY,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def get_pages(num_pages=None):

    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    # with open('db.json', 'w', encoding='utf8') as f:
    #    json.dump(data, f, ensure_ascii=False, indent=4)

    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])
        
    return results

def send_msg(alerts):
    beans = ' and '.join(alerts)

    if len(alerts) == 1:
        msg = f'{beans} is ready to use.'
    else:
        msg = f'{beans} are ready to use.'

    apobj = apprise.Apprise()
    hooks = list(config('NOTION_WEB_HOOKS').split(','))
    for i in hooks:
        apobj.add(i)
    
    apobj.notify(
        body=msg,
        # title='Bean Alert!',
    )

if __name__ == "__main__":
    pages = get_pages()
    now = datetime.now().strftime('%Y-%m-%d')
    alerts = []

    for page in pages:
        try:
            prop = page['properties']
            bean = prop['Name']['title'][0]['plain_text']
            roaster = prop['Roaster']['rich_text'][0]['plain_text']
            status = prop['Status']['status']['name']
            rest_date = prop['Rested date']['formula']['date']['start'] # 2024-09-24
        except:
            continue

        if status == 'Resting' and rest_date <= now:
            alerts.append(f'{roaster} {bean}')
    
    if alerts:
        send_msg(alerts)