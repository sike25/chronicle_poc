# dump_json.py

import pandas as pd
import json

# Load enriched data
df = pd.read_csv('nigerian_news_dataset/_enriched.csv')

# Parse dates
df['date_parsed'] = pd.to_datetime(df['date_parsed'])

# Group by query and bucket
data = {}

for query in df['query'].unique():
    query_df = df[df['query'] == query]
    
    buckets = []
    for bucket_id in sorted(query_df['bucket_id'].unique()):
        bucket_df = query_df[query_df['bucket_id'] == bucket_id]
        
        # Convert articles to list of dicts
        articles = []
        for _, row in bucket_df.iterrows():
            articles.append({
                'date': row['date'],
                'headline': row['headline'],
                'source': row['source'],
                'filename': row['filename']
            })
        
        buckets.append({
            'bucket_id': int(bucket_id),
            'bucket_label': bucket_df['bucket_label'].iloc[0],
            'bucket_title': bucket_df['bucket_title'].iloc[0],
            'bucket_summary': bucket_df['bucket_summary'].iloc[0],
            'article_count': len(bucket_df),
            'articles': articles
        })
    
    data[query] = {
        'total_articles': len(query_df),
        'date_range': {
            'min': query_df['date'].min(),
            'max': query_df['date'].max()
        },
        'buckets': buckets
    }

# Save as JSON
with open('demo/chronicle_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print("✓ Data exported to chronicle_data.json")
print(f"\nQueries available: {list(data.keys())}")
for query, query_data in data.items():
    print(f"  {query}: {query_data['total_articles']} articles, {len(query_data['buckets'])} buckets")