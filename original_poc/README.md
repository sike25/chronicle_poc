## Considering Chronicle

Chronicle is a proposed feature that extends [archivi.ng](https://archivi.ng/)’s search by providing a visual timeline of the original search results. The search results are grouped into periods, and each period cluster is summarized, titled and enriched with context.

### How It Works.
The notebook takes in a natural language query and collects all the news headlines in the dataset which are relevant to this query. These results are sorted by date, and displayed on a visual timeline.

<img width="1189" height="589" alt="image" src="https://github.com/user-attachments/assets/25f43ea1-1458-4b7f-ad90-30736d759066" />


### Technical Details
I used a dataset of over 1 million [Australian news headlines](https://www.kaggle.com/datasets/therohk/million-headlines) spanning 2003-2023 to simulate what Chronicle would do with Archivi.ng's Nigerian archives.
The implementation uses Google Cloud Discovery Engine for search, a CSV → JSONL → indexed datastore pipeline for data ingestion, and Matplotlib for timeline visualization. The sample includes 190,000 headlines (10,000 per year, randomly sampled) 

## Looking Forward 
The engineering document in this repo goes through the system design and technical details for the larger Chronicle project.
