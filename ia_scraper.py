import internetarchive
import json


def fetch_collection_items_details(collection_id, output_file):
    search = internetarchive.search_items(f'collection:{collection_id}')
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in search:
            identifier = result['identifier']
            item = internetarchive.get_item(identifier)

            views = item.metadata.get('downloads', 0)
            favorites = item.metadata.get('num_favorites', 0)
            meta = item.metadata
            meta['downloads'] = views + favorites
            meta['num_favorites'] = favorites

            print(json.dumps(item.metadata, ensure_ascii=False))
            json.dump(item.metadata, f, ensure_ascii=False)
            f.write('\n')


if __name__ == '__main__':
    fetch_collection_items_details('DeadAndCompany', 'shows.jsonl')
