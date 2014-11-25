#encoding: utf-8
from bs4 import BeautifulSoup

def parse_sticky_head(stickyHead):
	#direction = stickyHead.find("h2")
	results = []
	for container in stickyHead.find_all("div", {"class":"flight-day-container"}):
	
		flightTooltip = container.find("p", {"class":"selectFlightTooltip"})
		
		flightDate = flightTooltip.find("span", {"class": "flight-date"})
		
		arrival = flightDate["data-flight-arrival"]
		departure = flightDate["data-flight-departure"]
		fareSpan = flightTooltip.find("span", {"class": "flight-fare"})
		price = fareSpan.find("span", {"class":"original"}).string

		results.append( { "departure":departure, "arrival": arrival, "price": price} )
	return results

def parse_search_doc(html_doc):

	soup = BeautifulSoup(html_doc)
	cityTo = soup.find("input", {"class": "city-to"})["value"]
	cityFrom = soup.find("input", {"class": "city-from"})["value"]
	table = soup.find('div', {"class": "price-table"})
	stickyHeads = table.find_all("div", {"class": "stickyHead"})

	return {
		"from" : cityFrom,
		"to" : cityTo,
		
		"first": parse_sticky_head(stickyHeads[0]),
		"second":  parse_sticky_head(stickyHeads[1])
	}

