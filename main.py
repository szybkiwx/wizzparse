from wizzair_scraper import WizzairPage
from ryan_scraper import RyanPage
if __name__ == "__main__":
	departure_date = "2015-01-10"
	return_date = "2015-01-15"
	wizz = RyanPage()
	wizz.run(departure_date, return_date)