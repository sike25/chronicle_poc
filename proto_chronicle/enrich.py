import anthropic
import json
import random
from data.shape import EnrichedCluster

MODEL  = "claude-sonnet-4-20250514"

client = anthropic.Anthropic()
def enrich_clusters(clusters, query):
    enriched_clusters = {}
    for date, entries in clusters.items():
        title   = ""
        summary = ""
        
        # pick {nb_samples} random articles from each cluster
        # nb_samples = 2
        # random_indexes = set()
        # for i in range(nb_samples):
        #     random_indexes.add(i)
        # sampled_entries = [entries[idx] for idx in random_indexes]

        # extract relevant parts of the article, and make llm call for context
        print("Extracting and summarizing relevant documents....")
        print(f"\nTime period: {date}")
        for entry in entries:
            entry.source.relevant_extract = extract_relevant_portions(entry, query)
            print(f"\n----> Entry: {entry.source.filename}")
            print(f"-----------> Relevant Extract: \n-----------> {entry.source.relevant_extract}")
        title, summary = generate_bucket_context(query, entries, date)
        
        enriched_clusters[date] = EnrichedCluster(
            label=date,
            title=title,
            summary=summary,
            entries=entries,
            start_date=entries[0].source.publication_date,
            end_date=entries[0].source.publication_date,
        )
    return enriched_clusters


def extract_relevant_portions(entry, query):

    prompt = f"""You are analyzing an archived Nigerian newspaper article retrieved for the query: "{query}"

        DOCUMENT:
        Filename: {entry.source.filename}
        Publication: {entry.source.publication} ({entry.source.publication_date})
        Full Summary: {entry.source.summary}
        Full Extract: {entry.source.extract}

        TASK:
        Extract ONLY the portions of the article text that directly relate to "{query}"
        - Preserve specific details: dates, names, locations, numbers
        - Keep enough context to be understandable
        - If the entire article is relevant, include it all

        Return ONLY valid JSON (no markdown, no backticks):
        {{
            "relevant_extract": "extracted text here",
        }}"""

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = json.loads(response.content[0].text)
        
        if 'relevant_extract' not in result:
            raise KeyError("Missing required fields in response")
            
        return result['relevant_extract']
        
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error extracting from {entry.source.filename}: {e}")
        # Fallback: return original content
        return entry.source.summary, entry.source.extract


def generate_bucket_context(query, entries, dates):
    # Build entries text more efficiently
    entries_text = []
    for i, entry in enumerate(entries, 1):
        entries_text.append(f"""
            Entry {i}:
            Filename: {entry.source.filename}
            Extract: {entry.source.relevant_extract}
            ---""")
    
    context_generation_prompt = f"""You are analyzing {len(entries)} archived Nigerian newspapers from {dates} returned for the query: "{query}"

        Generate a comprehensive analysis:
        1. A brief, descriptive title (5-10 words) capturing the key themes
        2. A complete paragraph summary synthesizing the main patterns, events, and themes across all entries

        ENTRIES:
        {''.join(entries_text)}

        Return ONLY valid JSON (no markdown, no backticks):
        {{
            "title": "your title here",
            "summary": "your summary here"
        }}"""
    
    try:
        response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": context_generation_prompt}]
         )
    
        result = json.loads(response.content[0].text)
        if 'title' not in result or 'summary' not in result:
            raise KeyError("Missing required fields in response")
        return result['title'], result['summary']
        
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Error generating context: {e}")
        return f"Results for '{query}'", f"Collection of {len(entries)} articles from {dates} related to {query}."