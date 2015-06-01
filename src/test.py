import grequests
import requests
import gevent

gevent.monkey.patch_all(thread=False)
requests.packages.urllib3.disable_warnings()

# urls = ['http://httpbin.org/status/404', 'http://httpbin.org/status/302']

def get_urls_ary():
  tmp = open('/Users/brunomacedo/Desktop/NYU-Poly/3rd-Semester/Memex/code/freshness-crawler/input/urlsComplete.txt', "r")
  urls = map(lambda x: x.replace("\n", ""), tmp.readlines())
  tmp.close()
  return urls

def use_grequests():
  rqs = (grequests.get(url) for url in urls)
  for response in grequests.map(rqs):
    pass
    # print response

def worker_requests(url):
  response = requests.get(url, verify=False)


def use_gevent_requests():
  jobs = [gevent.spawn(worker_requests, url) for url in urls]
  gevent.joinall(jobs)

if __name__=='__main__':
  urls = get_urls_ary()
  # use_grequests()
  from timeit import Timer
  t = Timer(stmt="use_grequests()", setup="from __main__ import use_grequests")
  print 'by grequests: %s seconds'%t.timeit(number=3)
  t = Timer(stmt="use_gevent_requests()", setup="from __main__ import use_gevent_requests")
  print 'by gevent_requests: %s seconds'%t.timeit(number=3)