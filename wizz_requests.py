import requests

ssl_check_off = False

proxy_dict = {}
def post(url, data={}, headers={},cookies={}):
	verify = not ssl_check_off
	print "cookies", cookies
	return requests.post(url, data=data, headers=headers,cookies=cookies, proxies=proxy_dict, verify=verify)
	
def get(url, headers={},cookies={}):
	verify = not ssl_check_off
	return requests.get(url, headers=headers, cookies=cookies, proxies=proxy_dict, verify=verify)