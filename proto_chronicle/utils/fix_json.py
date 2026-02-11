import json

input_file = 'data/dump.json'
output_file = 'data/formatted_dump.jsonl'

with open(input_file, 'r', encoding='utf-8') as infile, \
     open(output_file, 'w', encoding='utf-8') as outfile:
    
    for line in infile:
        entry_data = json.loads(line)
        
        # 1. Clean the ID (Vertex doesn't like the leading underscore)
        doc_id = str(entry_data.get('_id', '')).replace('_', '-')
        
        # 2. Extract the actual content
        source_data = entry_data.get('_source', {})
        
        # 3. Build the Vertex AI compatible structure
        vertex_doc = {
            "id": doc_id,
            "structData": source_data  # This maps summary, extract, etc.
        }
        
        # Write as a single line
        outfile.write(json.dumps(vertex_doc) + '\n')