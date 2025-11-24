from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import anthropic
import base64
import json
import time
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Allow frontend to call API

# Configuration
IMAGE_FOLDER = "./nigerian_news_dataset/all_topics"
DATA_FILE = "./nigerian_news_dataset/_bucketed.csv"

def encode_image(image_path):
    """Convert image to base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def get_media_type(filename):
    """Determine media type from extension"""
    ext = filename.lower().split('.')[-1]
    if ext in ['jpg', 'jpeg']:
        return 'image/jpeg'
    elif ext == 'png':
        return 'image/png'
    else:
        return 'image/jpeg'

def generate_bucket_description(bucket_df, image_folder):
    """Use Claude to generate title + summary for a bucket"""
    client = anthropic.Anthropic()
    
    sample_images = bucket_df.sort_values('date_parsed')
    
    image_content = []
    for _, row in sample_images.iterrows():
        image_path = Path(image_folder) / row['filename']
        
        if not image_path.exists():
            print(f"  ⚠️  Image not found: {image_path}")
            continue
            
        image_data = encode_image(image_path)
        media_type = get_media_type(row['filename'])
        
        image_content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_data,
            }
        })
    
    if not image_content:
        return None, None
    
    # Add text prompt
    bucket_label = bucket_df['bucket_label'].iloc[0]
    query = bucket_df['query'].iloc[0]
    
    image_content.append({
        "type": "text",
        "text": f"""These are Nigerian newspaper articles from {bucket_label} about "{query}".

Generate:
1. A brief title (3-5 words) that captures the key theme
2. A 2-sentence summary of what was happening during this period

Return ONLY valid JSON with no additional text:
{{
    "title": "...",
    "summary": "..."
}}"""
    })
    
    # Call Claude
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": image_content
        }]
    )
    
    # Parse response
    response_text = message.content[0].text.strip()
    response_text = response_text.replace('```json', '').replace('```', '').strip()
    
    result = json.loads(response_text)
    return result['title'], result['summary']

@app.route('/api/search', methods=['GET'])
def search():
    """Step 1: Search archives (returns metadata)"""
    query = request.args.get('query')
    
    # Load data
    df = pd.read_csv(DATA_FILE)
    df['date_parsed'] = pd.to_datetime(df['date_parsed'])
    
    query_df = df[df['query'] == query]
    
    if len(query_df) == 0:
        return jsonify({'error': 'Query not found'}), 404
    
    return jsonify({
        'query': query,
        'documentCount': len(query_df),
        'dateRange': {
            'min': query_df['date'].min(),
            'max': query_df['date'].max()
        }
    })

@app.route('/')
def home():
    return jsonify({
        'status': 'Chronicle API is running!',
        'endpoints': [
            '/api/search?query=Fuel%20Subsidy',
            '/api/organize',
            '/api/enrich'
        ]
})

@app.route('/api/organize', methods=['POST'])
def organize():
    """Step 2: Organize into periods (returns buckets without enrichment)"""
    data = request.get_json()
    query = data['query']
    
    # Load data
    df = pd.read_csv(DATA_FILE)
    df['date_parsed'] = pd.to_datetime(df['date_parsed'])
    
    query_df = df[df['query'] == query]
    
    # Get unique buckets
    buckets = []
    for bucket_id in sorted(query_df['bucket_id'].unique()):
        bucket_df = query_df[query_df['bucket_id'] == bucket_id]
        
        buckets.append({
            'bucket_id': int(bucket_id),
            'bucket_label': bucket_df['bucket_label'].iloc[0],
            'article_count': len(bucket_df)
        })
    
    return jsonify({
        'query': query,
        'bucketCount': len(buckets),
        'buckets': buckets
    })

@app.route('/api/enrich', methods=['POST'])
def enrich():
    """Step 3: Generate summaries (THIS IS WHERE CLAUDE API COSTS HAPPEN!)"""
    data = request.get_json()
    query = data['query']
    
    # Load data
    df = pd.read_csv(DATA_FILE)
    df['date_parsed'] = pd.to_datetime(df['date_parsed'])
    
    query_df = df[df['query'] == query]
    
    # Enrich each bucket
    enriched_buckets = []
    
    for bucket_id in sorted(query_df['bucket_id'].unique()):
        bucket_df = query_df[query_df['bucket_id'] == bucket_id]
        
        print(f"Enriching {bucket_df['bucket_label'].iloc[0]}...")
        
        # THIS IS THE REAL-TIME CLAUDE API CALL!
        try:
            title, summary = generate_bucket_description(bucket_df, IMAGE_FOLDER)
        except Exception as e:
            print(f"Error: {e}")
            title = f"{bucket_df['bucket_label'].iloc[0]} Coverage"
            summary = f"Articles from {bucket_df['bucket_label'].iloc[0]}"
        
        # Build articles list
        articles = []
        for _, row in bucket_df.iterrows():
            articles.append({
                'date': row['date'],
                'headline': row['headline'],
                'source': row['source'],
                'filename': row['filename']
            })
        
        enriched_buckets.append({
            'bucket_id': int(bucket_id),
            'bucket_label': bucket_df['bucket_label'].iloc[0],
            'bucket_title': title,
            'bucket_summary': summary,
            'article_count': len(bucket_df),
            'articles': articles
        })
        
        time.sleep(0.5)  # Small delay between calls
    
    return jsonify({
        'query': query,
        'buckets': enriched_buckets
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)