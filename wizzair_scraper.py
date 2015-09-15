import re
from iata import get_relations
from scraper import Page
from bs4 import BeautifulSoup
import wizz_requests
import logging
import requests
import sys
class WizzairPage(Page):		
	
	def get_relations(self, start):
		return get_relations(start)

	def get_carrier(self):
		return "Wizzair"
	
	def get_flights(self, origin, destination, departure_date, return_date):
		logging.debug("origin :%s, destination: %s, departure_date: %s, return_date: %s", origin, destination, departure_date, return_date)
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Encoding": "gzip, deflate",
			"Cache-Control": "max-age=0",
			"Accept-Language": "pl-PL,pl;q=0.8,en-US;q=0.6,en;q=0.4",
			"Content-Type": "application/x-www-form-urlencoded"
		}
		
		search_url = "https://wizzair.com/pl-PL/FlightSearch"
		
		r = wizz_requests.get("https://wizzair.com/pl-PL/Search", headers=headers, allow_redirects=False)
		session_id = r.cookies["ASP.NET_SessionId"]

		cookies = {
			"ASP.NET_SessionId": session_id,
			"HomePageSelector":"FlightSearch",
		}
		
		r = wizz_requests.get(search_url, headers=headers, cookies=cookies)
		found = re.findall("<input id=\"viewState\" type=\"hidden\" value=\"(.*?)\" name=\"viewState\"><input type=\"hidden\" name=\"pageToken\" value=\"\"><input name=\"(.*?)\" type=\"hidden\" value=\"(.*?)\">", r.content)
		(view_state, name, value) = found[0]
		
		payload = {
			"__EVENTTARGET": "HeaderControlGroupRibbonSelectView_AvailabilitySearchInputRibbonSelectView_ButtonSubmit",
			"__VIEWSTATE": view_state,
			name: value,
			"ControlGroupRibbonAnonNewHomeView$AvailabilitySearchInputRibbonAnonNewHomeView$OriginStation": origin,
			"ControlGroupRibbonAnonNewHomeView$AvailabilitySearchInputRibbonAnonNewHomeView$DestinationStation": destination,
			"ControlGroupRibbonAnonNewHomeView$AvailabilitySearchInputRibbonAnonNewHomeView$DepartureDate": departure_date,
			"ControlGroupRibbonAnonNewHomeView$AvailabilitySearchInputRibbonAnonNewHomeView$ReturnDate": return_date,
			"ControlGroupRibbonAnonNewHomeView$AvailabilitySearchInputRibbonAnonNewHomeView$PaxCountADT": "1",
			"ControlGroupRibbonAnonNewHomeView$AvailabilitySearchInputRibbonAnonNewHomeView$PaxCountCHD": "0",
			"ControlGroupRibbonAnonNewHomeView$AvailabilitySearchInputRibbonAnonNewHomeView$PaxCountINFANT": "0",
			"ControlGroupRibbonAnonNewHomeView$AvailabilitySearchInputRibbonAnonNewHomeView$ButtonSubmit": "Szukaj"
		}
		cookies.update({
			"Culture": "pl-PL",
			"cookiesAccepted": "true",
			"cookie_settings": "necessary=1,functionality=1,performance=1,advertising=1",
			"__gfp_64b": "yTYgcfSZZM.6nNqHvL.gNGd.h3io.aR8iqEp07ehbm3.77"
		})
		
		headers["Origin"] = "https://wizzair.com"
		headers["Referer"] = search_url
		headers["Upgrade-Insecure-Requests"] = 1
		r = wizz_requests.post(search_url, headers=headers, cookies=cookies, data=payload)
		return self.parse_search_doc(r.content)

	def parse_market_column(self, market_column):
		#direction = stickyHead.find("h2")
		results = []
		flights = market_column.findAll("div", {"class":"flight-row"})
		for row in flights[1:]:
			if "disabled" not in row["class"]:
				flight_date = row.find("div", {"class": "flight-date"}).find("span")
				
				arrival = flight_date["data-flight-arrival"]
				departure = flight_date["data-flight-departure"]
				
				flight_tooltip = row.find("div", {"class" :"selectFlightTooltip"})
				
				fare_span = flight_tooltip.find("label", {"class": "flight-fare"})
				price = fare_span.string
				results.append( { "departure":departure, "arrival": arrival, "price": price.split()[0].replace(",", ".").replace("&nbsp;", "")} )
		return results

	def parse_search_doc(self, html_doc):
		with open("debug.txt", "w") as f:
			f.write(html_doc)
			
		soup = BeautifulSoup(html_doc)
		city_to = soup.find("input", {"class": "city-to"})["value"]
		city_from = soup.find("input", {"class": "city-from"})["value"]
		table = soup.find('div', {"class": "price-table"})

		market_column0 = table.find("div", {"id": "marketColumn0"})
		market_column1 = table.find("div", {"id": "marketColumn1"})
		
		#currency = soup.find("div", {"id": "priceDisplayBody"}).find("span", {"class": "ui-selectmenu-status"}).string
		
		#found = re.findall("Cena.*\((.*)\)", price_header, re.DOTALL)

		return {
			"from" : city_from,
			"to" : city_to,
			
			"first": self.parse_market_column(market_column0),
			"second":  self.parse_market_column(market_column1)#,
			#"currency": currency
		}

if __name__ == "__main__":
	w = WizzairPage()
	#http_proxy  = "http://proxy-chain.intel.com:911"
	#https_proxy = "https://proxy-chain.intel.com:912"
	#https_proxy = http_proxy  = "localhost:8888"
	#wizz_requests.proxy_dict = { 
	#	"http"  : http_proxy, 
	#	"https" : https_proxy
	#}
	
	wizz_requests.ssl_check_off = True
	logging.basicConfig(level=logging.DEBUG)
	print w.get_flights("GDN", "BCN", "2015-09-17", "2015-09-27")