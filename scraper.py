from parse_flights import parse_search_doc

import sqlite3
import multiprocessing.dummy as multiprocessing
import logging
import json 
import requests
logger = logging.getLogger("scrapper")

class Page:

	def get_carrier(self):
		pass

	def get_relations(self, start):
		pass
	
	def get_flights(self, src, dst, departure_date, return_date):
		logger.error("NotImplementedError")
		raise NotImplementedError();
	
	def check_course(self, fromC, toC):
		logger.debug("check_course" )
		q = 'https://query.yahooapis.com/v1/public/yql?q=select * from yahoo.finance.xchange where pair in ("%s%s")&format=json&diagnostics=true&env=store://datatables.org/alltableswithkeys&callback=' % (fromC, toC)
		logger.debug(q) 
		r = requests.get(q)
		return r.json()["query"]["results"]["rate"]["Rate"]
		
	def insert_flights(self, city_from, city_to, departure_date, return_date):
		logger.info("processing  %s -> %s:" %(city_from, city_to))
		logger.debug("get_flights" )
		flights = self.get_flights(city_from, city_to, departure_date, return_date)
		logger.debug("/get_flights: %s", json.dumps(flights) )
		conn = sqlite3.connect('flights.db')
		cursor = conn.cursor()
		
		
		
		for result in flights["first"]:
			try:
				price_pln = float(self.check_course(flights["currency"], "PLN")) * float(result["price"])
				cursor.execute("insert into flights (carrier, start, destination, departure, arrival, price, currency, price_pln) values (?, ?, ?, ?, ?, ?, ?, ?)", (self.get_carrier(), city_from, city_to, result["departure"], result["arrival"], result["price"], flights["currency"], price_pln))
			except sqlite3.IntegrityError:
				logger.info("flight already added")
			except sqlite3.Error as e:
				logger.error("An error occurred:", e.args[0])
				logger.error(json.dumps(result))
		for result in flights["second"]:
			try:
				price_pln = float(self.check_course(flights["currency"], "PLN")) * float(result["price"])
				cursor.execute("insert into flights (carrier, start, destination, departure, arrival, price, currency, price_pln) values (?, ?, ?, ?, ?, ?, ?, ?)", (self.get_carrier(), city_to, city_from, result["departure"], result["arrival"], result["price"], flights["currency"], price_pln))
			except sqlite3.IntegrityError:
				logger.info("flight already added")
			except sqlite3.Error as e:
				logger.error("An error occurred:", e.args[0])
				logger.error(json.dumps(result))
		conn.commit()
	
	
	def run(self, start, departure_date, return_date):
		first_jump = self.get_relations(start)
		second_jump_list = {city: self.get_relations(city) for city in first_jump} 
		
		p = multiprocessing.Pool(20)

		def insert(city):
			self.insert_flights(start, city, departure_date, return_date)
		print first_jump

		xs = p.map(insert, first_jump)
		
		
		
		for city_from, relations in second_jump_list.items():	
			def insert_jump2(city_to):
				self.insert_flights(city_from, city_to, departure_date, return_date)
			xs = p.map(insert_jump2, relations)

	
	


	

	
	
	
	
