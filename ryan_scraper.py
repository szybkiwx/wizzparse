from ryan_iata import route_data
from scraper import Page
import requests
import sys

import logging

import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig() 
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

class RyanPage(Page):
	def __init__(self):
		self._session_id = None

	def get_carrier(self):
		return "RyainAir"
		
	def _find_airport_name(self, city):
		next(x["name"] for x in route_data["airports"] if x["iataCode"] ==  city)

	def get_relations(self, city):
		return route_data["routes"][city]
		
	def get_flights(self, origin, destination, departure_date, return_date):
		my_config = {'verbose': sys.stderr}
		
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.65 Safari/537.36"
		}
		
		cookies = {
		}
		if not self._session_id is None:
			cookies["ASP.NET_SessionId"] = self._session_id
		
		dday, dmonth, dyear = departure_date.split("-")
		rday, rmonth, ryear = return_date.split("-")
		data = {
			"ADULT":	1,
			"sector1_d":	destination,
			"sector1_o":	"a"+origin,
			"sector_1_d":	dday,
			"sector_1_m":	dmonth + dyear,
			"sector_2_d":	rday,
			"sector_2_m":	rmonth + ryear,
			"tc":	"1",
			"travel_type":	"on",
			"acceptTerms":	"yes",
			"zoneDiscount":	"",
			"fromAirportName":	self._find_airport_name(origin),
			"toAirportIATA":	self._find_airport_name(destination),
			"dateFlightFromInput":	"%s/%s/%s" %(dmonth, dday, dyear),
			"dateFlightToInput":	"%s/%s/%s" %(rmonth, rday, ryear),
			"adultQuantityInput":	"More",
			"CHILD":	0,
			"INFANT":	0
		}
		r = requests.post("https://www.bookryanair.com/SkySales/Booking.aspx?culture=en-gb&lc=en-gb", headers=headers, data=data)
		if self._session_id is None:
			self._session_id = r.cookies["ASP.NET_SessionId"]
			cookies["ASP.NET_SessionId"] = self._session_id
			
		headers = {
			"X-Requested-With": "XMLHttpRequest",
			"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.65 Safari/537.36",
			"Referer": "https://www.bookryanair.com/SkySales/Booking.aspx?culture=en-gb&lc=en-gb"
		}
		r = requests.get("https://www.bookryanair.com/SkySales/Search.aspx", headers=headers, cookies=cookies)

			
		j = re.findall("FR.flightData = (.*);", r.content)[0]
		data = json.loads(j)
		result = {
			"from" : origin,
			"to" : destination,
		}
		result["first"] = self.parse_flight(data, origin + destination)
		result["second"] = self.parse_flight(data, destination + origin)
		
	def parse_flight(self, data, key):
		result = []
		for x in [date for date in data[key] if date[1] != []]:
			field = x[1][0]
			parts = field[4]["ADT"][1]
			price = sum(int(v) for k,v in parts.items())
			result.append({ "departure": "T".join(field[3][0]), "arrival": "T".join(field[3][1]), "price": price})	
	

		return result