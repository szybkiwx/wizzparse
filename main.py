from wizzair_scraper import WizzairPage
from ryan_scraper import RyanPage
import logging

logger = logging.getLogger("scrapper")
logging.basicConfig()
if __name__ == "__main__":
	logger.setLevel(logging.INFO)
	departure_date = "2015-01-10"
	return_date = "2015-01-15"
	clients = [ WizzairPage]
	for client in clients:
		c = client()
		c.run("GDN", departure_date, return_date)
	