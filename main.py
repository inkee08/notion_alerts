import requests, json
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

    return results

if __name__ == "__main__":
    pages = get_pages()

    for page in pages:
        page_id = page["id"]
        props = page["properties"]
        url = props["URL"]["title"][0]["text"]["content"]
        title = props["Title"]["rich_text"][0]["text"]["content"]
        published = props["Published"]["date"]["start"]
        published = datetime.fromisoformat(published)