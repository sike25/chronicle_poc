from datetime import timedelta

from datetime import timedelta

def cluster_by_stride(entries, nb_buckets=10):
    if not entries:
        return {}

    first_entry = entries[0].source
    last_entry  = entries[-1].source

    first_date = first_entry.publication_date.to_python_datetime()
    last_date  = last_entry.publication_date.to_python_datetime()

    duration = last_date - first_date

    print(f"First result: {first_entry.filename} on {first_date}")
    print(f"Last  result: {last_entry.filename}  on {last_date} ")
    print(f"The search results span {duration.days} days.")

    # handle short durations
    if duration < timedelta(days=30):
        label = f"{first_date} to {last_date}"
        return {label: entries}

    stride = duration / nb_buckets
    
    buckets = {}
    for i in range(nb_buckets):
        b_start = first_date + (stride * i)
        b_end   = first_date + (stride * (i + 1))
        
        label = f"{b_start} to {b_end}"
        buckets[label] = []
        
        for entry in entries:
            entry_date = entry.source.publication_date.to_python_datetime()
            
            # the very last bucket is inclusive of the last_date
            if i == nb_buckets - 1:
                if b_start <= entry_date <= last_date:
                    buckets[label].append(entry)
            else:
                if b_start <= entry_date < b_end:
                    buckets[label].append(entry)
        
    # drop empty clusters
    return {k: v for k, v in buckets.items() if v}
