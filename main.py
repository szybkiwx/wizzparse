from wizzair_scraper import WizzairPage
from ryan_scraper import RyanPage
from easyjet_scraper import EasyjetPage
import logging
import datetime

logger = logging.getLogger("scrapper")
logging.basicConfig()

class Runner:
	def __init__(self):
		self.clients = [RyanPage, WizzairPage, EasyjetPage]
		
		self.failed = []
	def start(self, threads):
		logger.setLevel(logging.DEBUG)
		date = datetime.date(2015, 4, 25)
		for i in [0, 3, 6, 9, 12]:
			departure_date = date.isoformat()
			date = date + datetime.timedelta(days=5)
			return_date = date.isoformat()
			
			for client in self.clients:
				c = client()
				c.run(threads, "GDN", departure_date, return_date)
		
		with open("failed.log", "w") as file:
			for f in self.failed:
				file.write(",".join([str(x) for x in f] ) +"\n")
				
if __name__ == "__main__":
	r = Runner()
	r.start(30)
	#x = EasyjetPage()	
	#x.debug()
		