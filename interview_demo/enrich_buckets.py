# encrich_buckets.py

import anthropic
import base64
import json
import pandas as pd
import time

from pathlib import Path

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
        return 'image/jpeg'  # default

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
    # Remove markdown code blocks if present
    response_text = response_text.replace('```json', '').replace('```', '').strip()
    
    result = json.loads(response_text)
    return result['title'], result['summary']

def enrich_buckets(df, image_folder):
    """Generate titles and summaries for all buckets"""
    results = []
    
    for query in df['query'].unique():
        query_df = df[df['query'] == query]
        
        print(f"\n📰 Processing {query}...")
        
        for bucket_id in sorted(query_df['bucket_id'].unique()):
            bucket_df = query_df[query_df['bucket_id'] == bucket_id]
            bucket_label = bucket_df['bucket_label'].iloc[0]
            
            print(f"  → {bucket_label} ({len(bucket_df)} articles)...", end=' ')
            
            try:
                title, summary = generate_bucket_description(bucket_df, image_folder)
                
                if title and summary:
                    bucket_df = bucket_df.copy()
                    bucket_df['bucket_title'] = title
                    bucket_df['bucket_summary'] = summary
                    print("✓")
                else:
                    print("⚠️ No images found")
                    bucket_df = bucket_df.copy()
                    bucket_df['bucket_title'] = f"{bucket_label} Coverage"
                    bucket_df['bucket_summary'] = f"Articles from {bucket_label}"
                
            except Exception as e:
                print(f"✗ Error: {e}")
                bucket_df = bucket_df.copy()
                bucket_df['bucket_title'] = f"{bucket_label} Coverage"
                bucket_df['bucket_summary'] = f"Articles from {bucket_label}"
            
            results.append(bucket_df)
            time.sleep(1)  # Rate limiting
    
    return pd.concat(results, ignore_index=True)

# Main execution
if __name__ == "__main__":
    # Load bucketed data
    df = pd.read_csv('./nigerian_news_dataset/_bucketed.csv')
    df['date_parsed'] = pd.to_datetime(df['date_parsed'])
    
    # Enrich buckets with titles and summaries
    IMAGE_FOLDER = "./nigerian_news_dataset/all_topics"
    print("🤖 Generating bucket descriptions with Claude...")
    df_enriched = enrich_buckets(df, IMAGE_FOLDER)
    
    # Save and print results
    df_enriched.to_csv('./nigerian_news_dataset/_enriched.csv', index=False)
    print("\n✓ Enrichment complete!")
    print("\nGenerated descriptions:")
    for _, row in df_enriched.drop_duplicates(['query', 'bucket_id']).iterrows():
        print(f"\n{row['query']} - {row['bucket_label']}:")
        print(f"  Title: {row['bucket_title']}")
        print(f"  Summary: {row['bucket_summary'][:100]}...")