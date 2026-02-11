from cluster       import cluster_by_stride
from data.shape    import Source, Entry, Date
from enrich        import enrich_clusters
from search        import search_data_dump
from utils.helpers import convertToDate

QUERY = "Election crises and violence"

# Search
print(f"Running search for `{QUERY}`...")
page_result = search_data_dump(search_query=QUERY, fake=True)
responses = []
try:
    for result in page_result:
        id     = result.document.id
        source = Source(
            summary           = result.document.struct_data["summary"],
            extract           = result.document.struct_data["extract"],
            filename          = result.document.struct_data["filename"],
            keywords          = result.document.struct_data["keywords"].split(","),
            image_path        = result.document.struct_data["image_path"],
            topics            = result.document.struct_data["topics"].split(","),
            publication       = result.document.struct_data["publication"],
            publication_date  = convertToDate(result.document.struct_data["publication_date"]),
            page              = result.document.struct_data["page"],
            tags              = result.document.struct_data["tags"].split(","),
        )

        response = Entry(
            id     = id,
            source = source,
        )
        responses.append(response)

except Exception as e:
    print(f"Retrieval error: {e}")
print("Done!")

nb_results = len(responses)
print(f"Retrieved {nb_results} results.")

# Sort
print("\n")
print("Sorting results by publication_date...")
responses.sort(key=lambda x: x.source.publication_date.to_python_datetime())
print("Done!")

# Cluster
print("\n")
print("Clustering results...")
clusters = cluster_by_stride(entries=responses)
print("Done!")

print("Clusters formed:")
for date, entries in clusters.items():
    print(f"{date}: {len(entries)} articles.")
    for entry in entries:
        print(f"---------> {entry.source.filename}")

# Enrichment
print("\n")
print("--------------------------------------------------------------")
print("Enriching clusters with context...")
enriched_clusters = enrich_clusters(clusters=clusters, query=QUERY)
print("Done!")

print("\n RESULTS FINAL")
print("Enriched Clusters:")
for date, enriched_cluster in enriched_clusters.items():
    print("\n")
    print(f"--> Enriched Cluster {enriched_cluster.label}:")
    print(f"------> Titled `{enriched_cluster.title}`")
    print(f"------> Summary: {enriched_cluster.summary}")
    print(f"------> Compiled from {len(enriched_cluster.entries)} sources")
    for entry in enriched_cluster.entries:
            print(f"-----------> {entry.source.filename}")

# Visualize








