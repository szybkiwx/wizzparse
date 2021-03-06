from parse_flights import parse_search_doc

import sqlite3
import multiprocessing.dummy as multiprocessing
import logging
import json 
import requests
import iata
import ryan_iata

logger = logging.getLogger("scrapper")

class Page:
	course_cache = {}
	
	def mid_points(self, start):
		points = iata.get_relations(start)
		points.extend(ryan_iata.get_relations(start))
		return points
		
	def get_carrier(self):
		pass

	def get_relations(self, start):
		pass
	
	def get_flights(self, src, dst, departure_date, return_date):
		logger.error("NotImplementedError")
		raise NotImplementedError();
	
	def check_course(self, fromC, toC):
		logger.debug("check_course" )
		if (fromC, toC) not in Page.course_cache:
			q = 'https://query.yahooapis.com/v1/public/yql?q=select * from yahoo.finance.xchange where pair in ("%s%s")&format=json&diagnostics=true&env=store://datatables.org/alltableswithkeys&callback=' % (fromC, toC)
			logger.debug(q) 
			r = requests.get(q)
			Page.course_cache[(fromC, toC)] = r.json()["query"]["results"]["rate"]["Rate"]
		return Page.course_cache[(fromC, toC)]
	
	def get_db_conn(self):
		return sqlite3.connect('flights.db')
	
	def insert_flights(self, city_from, city_to, departure_date, return_date):
		logger.info("processing  %s -> %s:" %(city_from, city_to))
		logger.debug("get_flights" )
		flights = self.get_flights(city_from, city_to, departure_date, return_date)
		logger.debug("/get_flights: %s", json.dumps(flights) )
		conn = self.get_db_conn();
		self.insert_to_db(conn, city_from, city_to, flights["first"], flights["currency"])
		self.insert_to_db(conn, city_to, city_from, flights["second"], flights["currency"])
		conn.commit()
		
	def insert_to_db(self, conn, city_from, city_to, flights, currency):
		cursor = conn.cursor()
		for result in flights:
			price_pln = float(self.check_course(currency, "PLN")) * float(result["price"])
			try:

				cursor.execute("insert into flights (carrier, start, destination, departure, arrival, price, currency, price_pln, created, updated) values (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)", (self.get_carrier(), city_from, city_to, result["departure"], result["arrival"], result["price"], currency, price_pln))
			except sqlite3.IntegrityError:
				logger.debug("flight already added")
				cursor.execute("update flights set price=?, price_pln=?,updated=CURRENT_TIMESTAMP where start=? and destination=? and departure=? and arrival=? ", ( result["price"], price_pln, city_from, city_to, result["departure"], result["arrival"]))
			except sqlite3.Error as e:
				logger.error("An error occurred:")
				logger.exception(e) 
				logger.error(json.dumps(result))
	
	def clear_old_flights(self, departure_date, return_date):
		conn = self.get_db_conn()
		c = conn.cursor()
		c.execute("delete from flights where departure >= ? and arrival <= ?", (departure_date, return_date))
		conn.commit()
		
	def run(self, threads, start, departure_date, return_date):
		
		#self.clear_old_flights(departure_date, return_date)
		first_jump = self.get_relations(start)
		second_jump_list = {city: self.get_relations(city) for city in self.mid_points(start)} 
		
		p = multiprocessing.Pool(threads)

		#if hasattr(self.runner, "DEBUG") and self.runner.DEBUG == True:
		
		def insert(city):
			for i in range(3):
				try:
					self.insert_flights(start, city, departure_date, return_date)
					break
				except Exception as e:
					logger.error("An error occurred inserting flights:")
					logger.exception(e) 
					#self.runner.failed.append((start, city, departure_date, return_date, e))

		xs = p.map(insert, first_jump)
	
		for city_from, relations in second_jump_list.items():	
			def insert_jump2(city_to):
				try:
					self.insert_flights(city_from, city_to, departure_date, return_date)
				except Exception as e:
					logger.error("An error occurred inserting flights:")
					logger.exception(e) 
					#self.runner.failed.append((city_from, city_to, departure_date, return_date, e))
			xs = p.map(insert_jump2, relations)

	