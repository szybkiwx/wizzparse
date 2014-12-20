#encoding: utf-8
import sqlite3
import json
import codecs

def run_query(conn, max_price):
	q = """select  f1.start, f1.destination, f2.destination, f1.departure, f2.arrival, f2.carrier, f1.price_pln + f2.price_pln  as p
	from flights f1 join flights f2 on f1.destination = f2.start 
	and strftime('%s', f2.departure) - strftime('%s', f1.arrival) between 3600 and 43200 and p < ?
	and f1.start = 'GDN'
	order by f1.departure;"""
	c = conn.cursor()
	c.execute(q, (max_price,))
	return c.fetchall()
	
conn = sqlite3.connect('flights.db')

rows = run_query(conn, 2500)
with codecs.open("iata.json", encoding='utf-8') as f:
	mapping = json.loads(f.read())

destinations = {}

result = ""
	
for row in rows:
	dst_code = row[2]
	
	if dst_code in mapping:
		country = mapping[dst_code]["country"]
		if country not in destinations:
			destinations[country] = {}
			
		if dst_code not in destinations[country]:
			destinations[country][dst_code] = []
			
		destinations[country][dst_code].append((row[3], row[4], row[5], row[6]))

		
for country, dst in destinations.items():
	result += "===========================================\n"
	result += country + "\n"
	result += "===========================================\n"
	for code, data in dst.items():
		try:
			result += mapping[code]["city"] + "\n"
			for e in data: 
				result += "\t".join([str(x) for x in e]) + "\n"
		except  UnicodeDecodeError:
			print code
			raise
f = codecs.open("result.txt", encoding='utf-8', mode="w")
f.write(result)