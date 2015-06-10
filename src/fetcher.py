import os
import urllib2
from datetime import timedelta
from datetime import datetime
import json
import ssl
import httplib
import socket
import requests
import gevent
from gevent import monkey
from gevent.pool import Pool

gevent.monkey.patch_all(thread=False)
requests.packages.urllib3.disable_warnings()

TIMEOUT_DOMAIN_FETCH = 0 # seconds
WAIT_SERVER_RESPONSE_TIME = 10 # how long to wait for a server response // 10s a 30s

class Fetcher(object):

  def __init__(self, url_file, run_number):
    self.url_file = url_file
    self.run_number = run_number

  def get_urls_ary(self):
    tmp = open(self.url_file, "r")
    urls = map(lambda x: x.replace("\n", ""), tmp.readlines())
    tmp.close()
    return urls

  def find_between(self, s, first, last):
    try:
      start = s.index(first) + len(first)
      end = s.index(last, start)
      return s[start:end]
    except ValueError:
      return ""

  def parse_domain(self, url):
    if "http://" in url:
      domain = self.find_between(url, "http://", "/");
    elif "https://":
      domain = self.find_between(url, "https://", "/");
    else:
      domain = ""
    return domain

  def get_urls(self):
    urls = {}
    urls_ary = self.get_urls_ary()
    for url in urls_ary:
      # url = urllib2.unquote(url)
      if url[:7] != "http://" and url[:8] != "https://": # use only if input urls doesn't have http/https in front of them
        url = "http://" + url
      domain = self.parse_domain(url)
      if domain not in urls:
        urls[domain] = { "urls" : [], "last_fetch" : datetime.now() - timedelta(0, TIMEOUT_DOMAIN_FETCH) }
      urls[domain]["urls"].append(url)
    return urls

  def next_fetch(self, urls):
    fetch_urls = []
    domains_to_remove = []
    for domain in sorted(urls): # ordenar dictionary
      while urls[domain]["last_fetch"] > datetime.now() - timedelta(0, TIMEOUT_DOMAIN_FETCH):
        pass
      fetch_urls.append(urls[domain]["urls"].pop())
      urls[domain]["last_fetch"] = datetime.now()
      if urls[domain]["urls"] == []:
        domains_to_remove.append(domain)
    for domain in domains_to_remove:
      del urls[domain]
    return fetch_urls

  def create_diretory(self, path):
    if not os.path.exists(path):
      os.makedirs(path)

  def save_response(self, url, response):
    self.create_diretory("tmp")
    tmp_dir = "tmp/run_" + str(self.run_number)
    self.create_diretory(tmp_dir)
    domain = self.parse_domain(url)
    path = tmp_dir + "/" + domain
    self.create_diretory(path)
    file_path = path + "/" + urllib2.quote(url, '')
    tmp = open(file_path, 'w+')
    tmp.write(response)
    tmp.close()

  # read response and return whatever is needed in the form of a stringified json
  def read_response(self, response):
    try:
      html = response.text
    except httplib.IncompleteRead as e:
      html = e.partial
    headers = response.headers
    status_code = response.status_code
    # print status_code
    response_dict = { "html" : html, "headers" : unicode(str(headers), "ISO-8859-1"), "status_code" : status_code, "timestamp" : datetime.now().strftime("%m/%d/%Y %H:%M:%S") }
    return json.dumps(response_dict)

  def gevent_worker(self, url, responses):
    try:
      response = requests.get(url, verify=False, timeout=WAIT_SERVER_RESPONSE_TIME)
      responses[url] = self.read_response(response)
      print len(responses), ":", url
      self.save_response(url, responses[url])
    except IOError:
      pass
    except AttributeError: # skip https sites with invalid ssl certificate
      pass
    # response.close() # close the responses, so they don't keep the socket open

  def fetch_urls_and_save(self, responses, urls):
    pool = Pool(200)
    for url in urls:
      pool.spawn(self.gevent_worker, url, responses)
    pool.join()
    # jobs = [gevent.spawn(self.gevent_worker, url, responses) for url in urls]
    # gevent.joinall(jobs)

  # def fetch_urls_and_save(self, responses, urls):
  #   requests = (grequests.get(url, timeout=WAIT_SERVER_RESPONSE_TIME) for url in urls)
  #   for response in grequests.map(requests, grequests.Pool(1)):
  #     # print response.status_code
  #     try:
  #       url = str(response.url)
  #       responses[url] = self.read_response(response)
  #       print len(responses), ":", url
  #       self.save_response(url, responses[url])
  #     except IOError:
  #       pass
  #     except AttributeError: # skip https sites with invalid ssl certificate
  #       pass
  #     response.close() # close the responses, so they don't keep the socket open

  def fetch_and_save_all(self, urls):
    print "Starting fetch number", str(self.run_number)
    responses = {}
    while urls != {}:
      next_fetch_urls = self.next_fetch(urls) # { "urls" : [url1, url2, .., urln], "last_fetch" : decreasing # of seconds }
      self.fetch_urls_and_save(responses, next_fetch_urls)
    print "Fetched", len(responses), "urls."
    return responses

  def run(self):
    urls = self.get_urls()  # [{domain : { "urls" : [url1, url2, .., urln], "last_fetch" : decreasing # of seconds }}]
    responses = self.fetch_and_save_all(urls)
    return responses

