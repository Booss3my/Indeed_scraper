import requests
from bs4 import BeautifulSoup
import random
import concurrent.futures

#get the list of free proxies
def getProxies():
    r = requests.get('https://free-proxy-list.net/')
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find('tbody')
    proxies = []
    for row in table:
        if row.find_all('td')[4].text =='elite proxy':
            proxy = ':'.join([row.find_all('td')[0].text, row.find_all('td')[1].text])
            proxies.append(proxy)
        else:
            pass
    return proxies

def check_health(proxy):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0'}
    try:
        r = requests.get('https://httpbin.org/ip', headers=headers, proxies={'http' : proxy,'https': proxy}, timeout=5)
        print(r.json(), r.status_code)
    except requests.ConnectionError as err:
        error = repr(err)
        return "dead"
    return proxy



def get_healthy_proxies():
    proxylist = getProxies()

    #check proxies
    with concurrent.futures.ThreadPoolExecutor() as executor:
            out = executor.map(check_health, proxylist)
    return [a for a in list(out) if a!="dead"]


