#encoding: utf-8
import sqlite3
import json
import codecs
from datetime import datetime, timedelta
MAX_PRICE = 1000
MIN_DAYS = 5
MAX_DAYS = 10
print_long_report = True 

with codecs.open("iata.json", encoding='utf-8') as f:
	mapping = json.loads(f.read())

country_filter = [
"Belgium", "Netherlands", "Poland", "United Kingdom", "Sweden", "Belgium", "Norway", "Ireland"
] 
def run_joint_query(conn, start, end, start_time, end_time, max_price):
	
	cond =  " and f2.destination='%s' " % end if end != "" else ""
	
	q = """select  f1.start, f1.destination, f2.destination, f1.departure, f2.arrival, f1.carrier, f2.carrier, f1.price_pln + f2.price_pln  as p
	from flights f1 
	join flights f2 on f1.destination = f2.start and (strftime('%s', f2.departure) - strftime('%s', f1.arrival))/3600 between 4 and 48 
	where f1.departure >= ? and f1.arrival <= ?  
	and p < ?
	and f1.start=? """
	q += cond
	q += """order by f1.departure;"""
	
	
	c = conn.cursor()
	c.execute(q, (datetime.strptime(start_time, "%Y-%m-%d"), datetime.strptime(end_time, "%Y-%m-%d"), max_price, start))
	return [list(x) for x in c.fetchall()]

def run_simple_query(conn, start, end, start_time, end_time, max_price):
	cond =  " and destination='%s' " % end if end != "" else ""
	q = """select  start, destination, departure, arrival, carrier, price_pln as p from flights
	where departure >= ? and arrival <= ?  
	and p < ?	and start = ? """
	q += cond
	q += """ order by departure;"""
	
	print q
	
	c = conn.cursor()
	c.execute(q, (datetime.strptime(start_time, "%Y-%m-%d"), datetime.strptime(end_time, "%Y-%m-%d"),max_price, start))
	return [list(x) for x in c.fetchall()]

def long_report(destinations, result_file):
	f = codecs.open(result_file, encoding='utf-8', mode="w")
	for country, dst in destinations.items():
		if country not in country_filter:
			f.write("===========================================\n")
			f.write( country + "\n")
			f.write( "===========================================\n")
			for code, data in dst.items():
				try:
					f.write(mapping[code]["city"] + "\n")
					for e in data: 
						f.write( "\t".join([str(x) for x in e[:-2]]) + "\n")
						returns = e[-1]
						for ret in returns:
							f.write( "\t->")
							f.write( "\t".join([str(x) for x in ret]) + "\n")
				except  UnicodeDecodeError:
					print code
					raise
			f.write("\n")
		
def short_report(destinations, result_file):
	f = codecs.open(result_file, encoding='utf-8', mode="w")
	for country, dst in destinations.items():
		f.write("===========================================\n")
		f.write( country + "\n")
		f.write( "===========================================\n")
		for code, data in dst.items():
			try:
				f.write(mapping[code]["city"] + "\n")
				
			except  UnicodeDecodeError:
				print code
				raise
		f.write("\n")	

def to_datetime(string):
	if len(string.split(":")) < 3:
		string += ":00"

	return datetime.strptime(string, "%Y-%m-%dT%H:%M:%S" )

def to_string(dt):
	string = dt.strftime("%Y-%m-%d")
	return string

def process_joint(conn, start, end, start_time, end_time, destinations):
	rows = run_joint_query(conn, start, end, start_time, end_time, MAX_PRICE)
	next_step_rows = []
	
	for row in rows:
		s = to_string(to_datetime(row[4]) + timedelta(days=MIN_DAYS))
		e = to_string(to_datetime(row[4]) + timedelta(days=MAX_DAYS))
		returns = run_joint_query(conn, row[2], start, s, e, MAX_PRICE)
		next_step_returns = []
		for ret in returns:
			ret[-1] += row[-1]
			if ret[-1] < MAX_PRICE:
				next_step_returns.append(ret)
		if len(next_step_returns) > 0:
			row.append(returns)
			next_step_rows.append(row)
		
	for row in next_step_rows:
		dst_code = row[2]
		if dst_code in mapping:
			country = mapping[dst_code]["country"]
			if country not in destinations:
				destinations[country] = {}
				
			if dst_code not in destinations[country]:
				destinations[country][dst_code] = []
				
			destinations[country][dst_code].append((row[3], mapping[row[1]]["city"], row[4], row[5], row[6], row[7], row[8]))

def process_single(conn, start, end, start_time, end_time, destinations):
	rows = run_simple_query(conn, start, end, start_time, end_time,  MAX_PRICE)
	next_step_rows = []
	for row in rows:
		s = to_string(to_datetime(row[3])+ timedelta(days=MIN_DAYS))
		e = to_string(to_datetime(row[3]) +  timedelta(days=MAX_DAYS))
		returns = run_simple_query(conn, row[1], start, s, e,  MAX_PRICE)
		next_step_returns = []
		for ret in returns:
			ret[-1] += row[-1]
			if ret[-1] < MAX_PRICE:
				next_step_returns.append(ret)
		if len(next_step_returns) > 0:
			row.append(returns)
			next_step_rows.append(row)
			
	for row in next_step_rows:
		dst_code = row[1]
		if dst_code in mapping:
			country = mapping[dst_code]["country"]
			if country not in destinations:
				destinations[country] = {}
				
			if dst_code not in destinations[country]:
				destinations[country][dst_code] = []
				
			destinations[country][dst_code].append((row[2], row[3], row[4], row[5], row[6]))

	
def main(start="GDN", end="", result_file="result.txt", start_time="1970-01-01", end_time="2035-01-01", single_only=False):		
	conn = sqlite3.connect('flights.db')
	destinations = {}
		
	process_joint(conn, start, end, start_time, end_time, destinations)
	process_single(conn, start, end, start_time, end_time, destinations)
	
	print "print result"
	if print_long_report:
		long_report(destinations, result_file)
	else:
		short_report(destinations, result_file)
	conn.close()

if __name__ == "__main__":
	start_time = "2015-04-25"
	end_time = "2015-05-10"
	main(start="GDN", end="", result_file="result.txt", start_time=start_time, end_time=end_time, single_only=False)
	#main("BUD", "GDN", "result2.txt")
