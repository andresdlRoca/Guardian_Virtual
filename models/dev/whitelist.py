# Read CSV 
import csv

whitelist = []

with open('top-1m.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        whitelist.append(row[1])

def check_url(url):
    if url in whitelist:
        return {"status": "Whitelist"}
    else:
        return {"status": "No en whitelist"}

