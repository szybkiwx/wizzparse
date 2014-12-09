import requests
import re
from iata import get_relations
from scraper import Page
from bs4 import BeautifulSoup

class WizzairPage(Page):		
	def __init__(self, runner):
		Page.__init__(self, runner)
		
	def get_relations(self, start):
		return get_relations(start)

	def get_carrier(self):
		return "Wizzair"
		
	def get_flights(self, origin, destination, departure_date, return_date):
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Encoding": "gzip, deflate, sdch",
			"Cache-Control": "no-cache",
			"Accept-Language": "pl-PL,pl;q=0.8,en-US;q=0.6,en;q=0.4",
			"Pragma": "no-cache"
		}
		r = requests.get("http://wizzair.com/pl-PL/Search",headers=headers)
		session_id = r.cookies["ASP.NET_SessionId"]

		found = re.findall("<input id=\"viewState\" type=\"hidden\" value=\"(.*?)\" name=\"viewState\"><input type=\"hidden\" name=\"pageToken\" value=\"\"><input name=\"(.*?)\" type=\"hidden\" value=\"(.*?)\">", r.content)
		(view_state, name, value) = found[0]

		payload = {
			"__EVENTTARGET":"ControlGroupRibbonAnonHomeView_AvailabilitySearchInputRibbonAnonHomeView_ButtonSubmit",
			"__VIEWSTATE":view_state,
			name: value,
			"ControlGroupRibbonAnonHomeView$AvailabilitySearchInputRibbonAnonHomeView$ButtonSubmit":"Szukaj",
			"ControlGroupRibbonAnonHomeView$AvailabilitySearchInputRibbonAnonHomeView$DepartureDate": departure_date,
			"ControlGroupRibbonAnonHomeView$AvailabilitySearchInputRibbonAnonHomeView$DestinationStation": destination,
			"ControlGroupRibbonAnonHomeView$AvailabilitySearchInputRibbonAnonHomeView$OriginStation": origin,
			"ControlGroupRibbonAnonHomeView$AvailabilitySearchInputRibbonAnonHomeView$PaxCountADT":	"1",
			"ControlGroupRibbonAnonHomeView$AvailabilitySearchInputRibbonAnonHomeView$PaxCountCHD":	"0",
			"ControlGroupRibbonAnonHomeView$AvailabilitySearchInputRibbonAnonHomeView$PaxCountINFANT":"0",
			"ControlGroupRibbonAnonHomeView$AvailabilitySearchInputRibbonAnonHomeView$ReturnDate": return_date,
			"cookiePolicyDismissed":"true"
		}

		cookies = {
			"ASP.NET_SessionId":session_id,
			"HomePageSelector":"Search",
			"Culture": "pl-PL",
			"cookiesAccepted": "true",
			"__gfp_64b":"XPK3pghaNyGXZac.lTOwiY52hQedHWBeHDTS8.Q7o2H.w7",
			"cookie_settings": "necessary=1,functionality=1,performance=1,advertising=1"
		}
		
		headers["Origin"] = "http://wizzair.com"
		headers["Referer"] = "http://wizzair.com/pl-PL/Search"
	
		
		r = requests.post("http://wizzair.com/pl-PL/Search", headers=headers, cookies=cookies, data=payload)
		return self.parse_search_doc(r.content)

	def parse_sticky_head(self, sticky_head):
		#direction = stickyHead.find("h2")
		results = []
		for container in sticky_head.find_all("div", {"class":"flight-day-container"}):
		
			flight_tooltip = container.find("p", {"class":"selectFlightTooltip"})
			
			flight_date = flight_tooltip.find("span", {"class": "flight-date"})
			
			arrival = flight_date["data-flight-arrival"]
			departure = flight_date["data-flight-departure"]
			fare_span = flight_tooltip.find("span", {"class": "flight-fare"})
			price = fare_span.find("span", {"class":"original"}).string

			results.append( { "departure":departure, "arrival": arrival, "price": price.split()[0].replace(",", ".")} )
		return results

	def parse_search_doc(self, html_doc):
		with open("debug.txt", "w") as f:
			f.write(html_doc)
			
		soup = BeautifulSoup(html_doc)
		city_to = soup.find("input", {"class": "city-to"})["value"]
		city_from = soup.find("input", {"class": "city-from"})["value"]
		table = soup.find('div', {"class": "price-table"})
		sticky_heads = table.find_all("div", {"class": "stickyHead"})
		price_header = sticky_heads[0].find("span", {"class":"flight-fare"}).string
		
		found = re.findall("Cena.*\((.*)\)", price_header, re.DOTALL)

		return {
			"from" : city_from,
			"to" : city_to,
			
			"first": self.parse_sticky_head(sticky_heads[0]),
			"second":  self.parse_sticky_head(sticky_heads[1]),
			"currency":found[0]
		}
