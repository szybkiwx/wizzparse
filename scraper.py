from parse_flights import parse_search_doc
from bs4 import BeautifulSoup
import sqlite3

class Page:

	def get_carrier(self):
		pass

	def get_relations(self, start):
		pass
	
	def get_flights(self, src, dst, departure_date, return_date):
		pass
	
	def insert_flights(self, conn, city_from, city_to, departure_date, return_date):
		flights = self.get_flights(city_from, city_to, departure_date, return_date)
		cursor = conn.cursor()

		for result in flights["first"]:
			try:
				cursor.execute("insert into flights (carrier, start, destination, departure, arrival, price) values (?, ?, ?, ?, ?, ?)", (self.get_carrier(), city_from, city_to, result["departure"], result["arrival"], result["price"]))
			except sqlite3.IntegrityError:
				print "flight already added"
		for result in flights["second"]:
			try:
				cursor.execute("insert into flights (carrier, start, destination, departure, arrival, price) values (?, ?, ?, ?, ?, ?)", (self.get_carrier(), city_to, city_from, result["departure"], result["arrival"], result["price"]))
			except sqlite3.IntegrityError:
				print "flight already added"
				
		conn.commit()
		
	
	def run(self, departure_date, return_date):
		first_jump = self.get_relations("GDN")
		second_jump_list = {city: self.get_relations(city) for city in first_jump} 
		conn = sqlite3.connect('flights.db')
		print "first jump"
		for city in first_jump:
			print "GDN", city
			self.insert_flights(conn, "GDN", city, departure_date, return_date)

		print "second jump"
		for city_from, relations in second_jump_list.items():	
			for city_to in relations:
				print city_from, city_to
				self.insert_flights(conn, city_from, city_to, departure_date, return_date)
	
	


	

	
	
	
	
