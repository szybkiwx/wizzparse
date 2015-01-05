from scraper import Page
import easy_iata
import datetime
import sys
import re
import requests
import json 
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger("scrapper")

class EasyjetPage(Page):
		
	def get_carrier(self):
		return "EasyJet"

	def get_relations(self, start):
		return easy_iata.get_relations(start)
		

	def get_flights(self, src, dst, departure_date, return_date):
		headers = {}
		#/links.mvc?dep=KRK&dest=BFS&dd=1/12/2014&rd=4/12/2014&apax=1&pid=www.easyjet.com&cpax=0&ipax=0&lang=PL&isOneWay=off&searchFrom=SearchPod|/pl/ 
		url = "http://www.easyjet.com/links.mvc?dep=%s&dest=%s&dd=%s&rd=%s&apax=1&pid=www.easyjet.com&cpax=0&ipax=0&lang=PL&isOneWay=off&searchFrom=SearchPod|/pl/" %(src, dst, departure_date.replace("-", "/"), return_date.replace("-", "/"))
		logger.debug(url)
		r = requests.get(url)

		found = re.findall("var lookAndBookParams = (.*) ;\r", r.content)
		
		logger.debug("found: ")
		logger.debug(found)
		
		
		currency = json.loads(found[0])["Currency"]
		logger.debug("currency: "+currency )
		result = {
			"from" : src,
			"to" : dst,
			"currency": currency
		}
		
		soup = BeautifulSoup(r.text)
		
		slider = soup.find("div", {"class":"OutboundDaySlider"})
		result["first"] = list(self.process_slider(slider, departure_date, return_date)) if slider is not None else []
		slider = soup.find("div", {"class":"ReturnDaySlider"})
		result["second"] = list(self.process_slider(slider, departure_date, return_date)) if slider is not None else []
		return result

		
	def process_slider(self, slider, departure_date, return_date):
		for day in slider.find_all("div", {"class": "day"}):
		
			for li in day.find_all("li", {"class": "selectable"}):
				price_span = li.find("span", {"class": "priceSmaller"})
				if price_span is not None:
					second_part = price_span.find("span").string
					
					dep, arr = li.find_all("span", {"class": "time"})
					yield {
						"departure": "%sT%s:00" % (departure_date, dep.find_all("span")[2].string),
						"arrival": "%sT%s:00" % (return_date, arr.find_all("span")[2].string),
						"price": "%s.%s" %(price_span.contents[0].strip(), second_part)
					}
	def debug(self):
		print self.get_flights("EDI", "TFS", "2015-10-01", "2015-10-05")