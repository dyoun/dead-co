import internetarchive
import json
import requests

VIEWS_URL = "https://be-api.us.archive.org/views/v1/short/"


def fetch_collection_items_details(collection_id, output_file):
    search = internetarchive.search_items(f'collection:{collection_id}')
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in search:
            identifier = result['identifier']
            item = internetarchive.get_item(identifier)

            meta = item.metadata
            views = get_views(identifier)
            meta['views'] = views
            meta['views_all_time'] = views.get(identifier).get('all_time')
            meta['views_last_30day'] = views.get(identifier).get('last_30day')
            meta['views_last_7day'] = views.get(identifier).get('last_7day')
            # meta['num_favorites'] = favorites

            print(json.dumps(meta, ensure_ascii=False))
            json.dump(meta, f, ensure_ascii=False)
            f.write('\n')


def get_views(identifier):
    url = VIEWS_URL + identifier
    response = requests.get(url)
    views = response.json()

    return views

if __name__ == '__main__':
    fetch_collection_items_details('DeadAndCompany', 'shows.jsonl')
