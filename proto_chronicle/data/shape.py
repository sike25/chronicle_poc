from datetime import date

class Date():
    def __init__(self, day, month, year):
        self.day   = day
        self.month = month
        self.year  = year

    def __str__(self):
        return f"{self.year}/{self.month}/{self.day}"
    
    def __repr__(self):
        return self.__str__()
    
    def __lt__(self, other):
        # sort by year, then month, then day
        if self.year != other.year:
            return self.year < (other.year)
        if self.month != other.month:
            return self.month < other.month
        return self.day < other.day
    
    def to_python_datetime(self):
        return date(self.year, self.month, self.day)

class Source():
    def __init__(self, summary, extract, filename, keywords, image_path, topics, publication, publication_date: Date, page, tags):
        self.summary          = summary
        self.extract          = extract
        self.filename         = filename
        self.keywords         = keywords
        self.image_path       = image_path
        self.topics           = topics
        self.publication      = publication
        self.publication_date = publication_date
        self.page             = page
        self.tags             = tags

        # populated via llm call during enrichment
        # TODO (ogieva): extend search to return relevant extract
        self.relevant_summary = ""
        self.relevant_extract = ""

    def __str__(self):
        return f"""
        Source:
            {self.filename} \n
            -----
            {self.summary}
        """
    
    def __repr__(self):
        return self.__str__()

class Entry():
    def __init__(self, id, source: Source):
        self.id     = id
        self.source = source

    def __str__(self):
        return f"Entry(id = {self.id})\n  └── {self.source}"
    
    def __repr__(self):
        return self.__str__()
    
class EnrichedCluster():
    def __init__(self, label, title, summary, entries, start_date, end_date):
        self.label      = label
        self.title      = title
        self.summary    = summary
        self.entries    = entries
        self.start_date = start_date
        self.end_date   = end_date