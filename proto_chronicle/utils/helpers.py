from data.shape import Date

def convertToDate(date_string):
   date_split = date_string.split("/")
   return Date(
       day   = int(date_split[2]),
       month = int(date_split[1]),
       year  = int(date_split[0]),
   )