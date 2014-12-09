from wizzair_scraper import WizzairPage
from ryan_scraper import RyanPage
from easyjet_scraper import EasyjetPage
import logging
import datetime

logger = logging.getLogger("scrapper")
logging.basicConfig()

class Runner:
	def __init__(self, threads):
		self.threads = threads
		self.clients = [RyanPage, WizzairPage, EasyjetPage]
		self.failed = []
	def start(self):
		logger.setLevel(logging.INFO)
		date = datetime.date(2015, 2, 1)
		
		
		#clients= [RyanPage]
		for i in range(0, 31, 5):
			departure_date = date.isoformat()
			date = date + datetime.timedelta(days=5)
			return_date = date.isoformat()
			
			for client in self.clients:
				c = client(self)
				c.run("GDN", departure_date, return_date)
		
		with open("failed.log", "w") as file:
			for f in self.failed:
				file.write(",".join([str(x) for x in f] ) +"\n")
				
if __name__ == "__main__":
	r = Runner(20)
	r.start()
			
		