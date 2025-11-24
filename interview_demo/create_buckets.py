# create_buckets.py

import pandas as pd
from datetime import datetime

def parse_date(date_str):
    """Convert DD/MM/YYYY to datetime"""
    return pd.to_datetime(date_str, format='%d/%m/%Y')

def calculate_bucket_size(min_date, max_date):
    """Determine bucket granularity based on timespan"""
    timespan_years = (max_date - min_date).days / 365.25
    
    if timespan_years > 50:
        return 'decade'
    elif timespan_years > 20:
        return '5year'
    elif timespan_years > 10:
        return 'year'
    else:
        return 'month'

def assign_bucket(date, bucket_size):
    """Assign a document to its temporal bucket"""
    if bucket_size == 'decade':
        bucket_start = (date.year // 10) * 10
        return (bucket_start, f"{bucket_start}s")
    
    elif bucket_size == '5year':
        bucket_start = (date.year // 5) * 5
        return (bucket_start, f"{bucket_start}-{bucket_start+4}")
    
    elif bucket_size == 'year':
        return (date.year, str(date.year))
    
    elif bucket_size == 'month':
        return (date.strftime('%Y-%m'), date.strftime('%B %Y'))

def create_buckets(df):
    """Main function: add bucket columns to dataframe"""
    # Parse dates
    df['date_parsed'] = df['date'].apply(parse_date)
    
    # Process each query separately
    results = []
    
    for query in df['query'].unique():
        query_df = df[df['query'] == query].copy()
        
        # Calculate bucket size for this query
        min_date = query_df['date_parsed'].min()
        max_date = query_df['date_parsed'].max()
        bucket_size = calculate_bucket_size(min_date, max_date)
        
        print(f"\n{query}:")
        print(f"  Timespan: {min_date.year} - {max_date.year}")
        print(f"  Bucket size: {bucket_size}")
        
        # Assign buckets
        query_df[['bucket_id', 'bucket_label']] = query_df['date_parsed'].apply(
            lambda d: pd.Series(assign_bucket(d, bucket_size))
        )
        
        results.append(query_df)
    
    # Combine back together
    return pd.concat(results, ignore_index=True)

# Load your CSV
df = pd.read_csv('nigerian_news_dataset/_dataset.csv')

# Create buckets
df_bucketed = create_buckets(df)

# Save
df_bucketed.to_csv('nigerian_news_dataset/_bucketed.csv', index=False)