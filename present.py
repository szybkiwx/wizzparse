#encoding: utf-8
import sqlite3
import json
import codecs
from datetime import datetime, timedelta
MAX_PRICE = 600
MIN_DAYS = 3
MAX_DAYS = 6
print_long_report = True 

with codecs.open("iata.json", encoding='utf-8') as f:
	mapping = json.loads(f.read())

country_filter = [
"Belgium", "Netherlands", "Poland", "United Kingdom", "Sweden", "Belgium", "Norway", "Ireland"
] 
def run_joint_query(conn, start, end, start_time, end_time, max_price):
	
	cond =  " and f2.destination='%s' " % end if end != "" else ""
	
	q = """select  f1.start as start, f1.destination as middestination, f2.destination as destination, f1.departure departure, f2.arrival as arrival, f1.carrier as carrier_one, f2.carrier as carrier_two, f1.price_pln + f2.price_pln  as price2
	from flights f1 
	join flights f2 on f1.destination = f2.start and (strftime('%s', f2.departure) - strftime('%s', f1.arrival))/3600 between 3 and 8 
	where f1.departure >= ? and f1.arrival <= ?  
	and price2 < ?
	and f1.start=? """
	q += cond
	q += """order by f1.departure;"""
	
	
	c = conn.cursor()
	
	c.execute(q, (datetime.strptime(start_time, "%Y-%m-%d"), datetime.strptime(end_time, "%Y-%m-%d"), max_price, start))
	return c.fetchall()

def run_simple_query(conn, start, end, start_time, end_time, max_price):
	cond =  " and destination='%s' " % end if end != "" else ""
	q = """select  start, destination, departure, arrival, carrier, price_pln as price2 from flights
	where departure >= ? and arrival <= ?  
	and price2 < ?	and start = ? """
	q += cond
	q += """ order by departure;"""
	
	c = conn.cursor()
	c.execute(q, (datetime.strptime(start_time, "%Y-%m-%d"), datetime.strptime(end_time, "%Y-%m-%d"),max_price, start))
	return c.fetchall()

def long_report(conn, destinations):
	conn.execute("delete from analytics_view")
	conn.commit()
	q = "insert into analytics_view (country, city, departure, middestination, arrival, carrier_one, carrier_two, price, ret_departure, ret_middestination, ret_arrival, ret_carrier_one, ret_carrier_two, ret_price) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
	conn.executemany(q, destinations)
	conn.commit()
	
def short_report(destinations, result_file):
	f = codecs.open(result_file, encoding='utf-8', mode="w")
	for country, dst in destinations.items():
		f.write("============= ==============================\n")
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
	
	for row in rows:
		
		s = to_string(to_datetime(row[4]) + timedelta(days=MIN_DAYS))
		e = to_string(to_datetime(row[4]) + timedelta(days=MAX_DAYS))
		returns = run_joint_query(conn, row[2], start, s, e, MAX_PRICE)
		if row["destination"] in mapping:
			base = clean_row_joint(row)
			for ret in returns:
				if ret["destination"] in mapping:
					final_row = base[:]	 
					final_row.extend(clean_row_joint(ret)[2:])
					destinations.append(final_row)
			
			
def clean_row_joint(row):
	dst = row["destination"]
	mid =  row["middestination"]
	return [mapping[dst]["country"], mapping[dst]["city"], row["departure"], mapping[mid]["city"], row["arrival"], row["carrier_one"], row["carrier_two"], row["price2"]]
		
			
def process_single(conn, start, end, start_time, end_time, destinations):
	rows = run_simple_query(conn, start, end, start_time, end_time,  MAX_PRICE)
	for row in rows:
		s = to_string(to_datetime(row[3])+ timedelta(days=MIN_DAYS))
		e = to_string(to_datetime(row[3]) +  timedelta(days=MAX_DAYS))
		dst = row[1]
		returns = run_simple_query(conn, dst, start, s, e,  MAX_PRICE)
		if row["destination"] in mapping:
			base = clean_row_single(row)
			for ret in returns:
				if ret["destination"] in mapping:
					final_row = base[:]
					final_row.extend(clean_row_single(ret)[2:])
					destinations.append(final_row)
			
def clean_row_single(row):
	dst = row["destination"]
	return [mapping[dst]["country"], mapping[dst]["city"], row["departure"], "", row["arrival"], row["carrier"], "", row["price2"]]
	
def main(start="GDN", end="", result_file="result.txt", start_time="1970-01-01", end_time="2035-01-01", single_only=False):		
	conn = sqlite3.connect('flights.db')
	conn.row_factory = sqlite3.Row
	destinations = []
		
	process_joint(conn, start, end, start_time, end_time, destinations)
	process_single(conn, start, end, start_time, end_time, destinations)
	
	print "print result"
	if print_long_report:
		long_report(conn, destinations)
	else:
		short_report(destinations, result_file)
	conn.close()

if __name__ == "__main__":
	start_time = "2015-04-25"
	end_time = "2015-05-08"
	main(start="GDN", end="", result_file="result.txt", start_time=start_time, end_time=end_time, single_only=False)
	#main("BUD", "GDN", "result2.txt")
