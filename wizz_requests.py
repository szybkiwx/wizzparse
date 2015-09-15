import requests

ssl_check_off = False

proxy_dict = {}
def post(url, data={}, headers={},cookies={}, allow_redirects=True):
	verify = not ssl_check_off
	return requests.post(url, data=data, headers=headers,cookies=cookies, proxies=proxy_dict, verify=verify, allow_redirects=allow_redirects)
	
def get(url, headers={},cookies={}, allow_redirects=True):
	verify = not ssl_check_off
	return requests.get(url, headers=headers, cookies=cookies, proxies=proxy_dict, verify=verify, allow_redirects=allow_redirects)