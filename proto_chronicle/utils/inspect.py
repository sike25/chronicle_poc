import json
import sys

class Source():
    def __init__(self, summary, extract, filename, keywords, image_path, topics, publication, publication_date, page, tags):
        self.summary     = summary
        self.extract     = extract
        self.filename    = filename
        self.keywords    = keywords
        self.image_path  = image_path
        self.topics      = topics
        self.publication = publication
        self.pub_date    = publication_date
        self.page        = page
        self.tags        = tags

class Entry():
    def __init__(self, index, id, score, source: Source):
        self.index  = index
        self.id     = id
        self.score  = score
        self.source = source


def read_json(file_path):
    """
    Read a JSON file and transform into a (dataframe, list of objects?)
    
    Args:
        file_path: Path to the JSON file
    """
    idx = 0
    target = 12
    try: 
        with open(file=file_path, mode='r', encoding='utf-8') as file:
            for line in file:
                entry_data = json.loads(line)
                source_data = entry_data.get('_source', {})
                
                # Create Source object
                source = Source(
                    summary=source_data.get('summary'),
                    extract=source_data.get('extract'),
                    filename=source_data.get('filename'),
                    keywords=source_data.get('keywords'),
                    image_path=source_data.get('image_path'),
                    topics=source_data.get('topics'),
                    publication=source_data.get('publication'),
                    publication_date=source_data.get('publication_date'),
                    page=source_data.get('page'),
                    tags=source_data.get('tags')
                )
                
                # Create Entry object
                entry = Entry(
                    index=entry_data.get('_index'),
                    id=entry_data.get('_id'),
                    score=entry_data.get('_score'),
                    source=source
                )
                
                if idx == target:
                    return entry
                idx += 1
    except Exception as e:
        print(f"Error reading data dump: {e}")

    
entry = read_json('../data/dump.json')

print("Entry:")
print("---- id:   ", entry.id)
print("---- index:", entry.index)
print("---- score:", entry.score)
print("---- source:")
print("------------ filename:   ", entry.source.filename)
print("------------ publication:", entry.source.publication)
print("------------ pub_date:   ", entry.source.pub_date)
print("------------ page:       ", entry.source.page)
print("------------ image_path: ", entry.source.image_path)
print("------------ keywords:   ", entry.source.keywords)
print("------------ tags:       ", entry.source.tags)
print("------------ topics:     ", entry.source.topics)
print("------------ summary:    ", entry.source.summary)
print("------------ extract:    ", entry.source.extract)

