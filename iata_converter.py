import json
airports = {}

with open("iata.txt") as f:
	
	for line in f.readlines():
		(code, city, country) = line.strip().split("\t")
		airports[code] = ({
			"code": code,
			"city": city,
			"country": country
		})
		
with open("iata.json", "w") as f:
	f.write(json.dumps(airports, indent=4))
