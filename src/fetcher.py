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
from bs4 import BeautifulSoup
import re
# from multiprocessing import cpu_count
# from multiprocessing.dummy import Pool as ThreadPool

gevent.monkey.patch_all(thread=False)
requests.packages.urllib3.disable_warnings()

TIMEOUT_DOMAIN_FETCH = 0 # seconds
WAIT_SERVER_RESPONSE_TIME = 10 # how long to wait for a server response // 10s a 30s

REGEX_CLASSIFIER = False
REGEX_WORD = r'ebola'

# NUMBER_OF_CORES = cpu_count()

class Fetcher(object):

  def __init__(self, url_file, run_number):
    self.url_file = url_file
    self.run_number = run_number
    self.urls_cnt = 0
    self.fetched_urls_cnt = 0

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

  def test_regex(self, html, url):
    try:
      title = str(BeautifulSoup(html).title)
      regex = re.compile(REGEX_WORD, re.IGNORECASE)
      if regex.search(title) or regex.search(url): # test if title contains the word tested
        return True
      else:
        return False
    except httplib.IncompleteRead:
      return False

  # read response and return whatever is needed in the form of a stringified json
  def read_response(self, response, url):
    try:
      html = response.text
    except httplib.IncompleteRead as e:
      html = e.partial
    if REGEX_CLASSIFIER:
      if not self.test_regex(html, url):
        return False # return false if it doesn't pass regex test
    headers = unicode(str(response.headers), "ISO-8859-1")
    status_code = response.status_code
    final_url = unicode(str(response.url), "ISO-8859-1")
    # print status_code
    response_dict = { "html" : html, "headers" : headers, "status_code" : status_code, "timestamp" : datetime.now().strftime("%m/%d/%Y %H:%M:%S"), "url" : final_url }
    return json.dumps(response_dict)

  def url_handler(self, url): # reads response, test regex and save html in json format
    try:
      response = requests.get(url, verify=False, timeout=WAIT_SERVER_RESPONSE_TIME)
      response_json = self.read_response(response, url)
      response.close() # close the responses, so they don't keep the socket open
      self.urls_cnt += 1
      if response_json: # proceed if regex test passed
        self.fetched_urls_cnt += 1
        print self.fetched_urls_cnt, "/", self.urls_cnt, ":", url
        # print url
        self.save_response(url, response_json)
      else:
        print self.fetched_urls_cnt, "/", self.urls_cnt, "(regex failed):", url
        # print "regex failed:", url
    except IOError:
      pass
    except AttributeError: # skip https sites with invalid ssl certificate
      pass

  # def urls_chunk_handler(self, urls):
  #   for url in urls:
  #     self.url_handler(url)

  # def url_splitter(self, urls, cores=NUMBER_OF_CORES):
  #   urls_chunks = [[] for x in range(cores)]
  #   while urls:
  #     for i in range(cores):
  #       if urls:
  #         urls_chunks[i].append(urls.pop(0))
  #   return urls_chunks

  def fetch_urls_and_save(self, urls):
    # # using multiprocess threads
    # pool = ThreadPool(2 * NUMBER_OF_CORES)
    # pool.map(self.url_handler, urls)
    # pool.close()
    # pool.join()
    # # using multiprocess
    # urls_chunks = self.url_splitter(urls)
    # jobs = []
    # for urls_chunk in urls_chunks:
    #   j = multiprocessing.Process(target=self.urls_chunk_handler, args=(urls_chunk,))
    #   jobs.append(j)
    #   j.start()
    # for j in jobs:
    #   j.join()
    # # using gevent pool
    # pool = Pool(200)
    # for url in urls:
    #   pool.spawn(self.url_handler, url)
    # pool.join()
    # # using gevent spawn
    jobs = [gevent.spawn(self.url_handler, url) for url in urls]
    gevent.joinall(jobs)

  def fetch_and_save_all(self, urls):
    print "Starting fetch number", str(self.run_number)
    while urls != {}:
      next_fetch_urls = self.next_fetch(urls) # { "urls" : [url1, url2, .., urln], "last_fetch" : decreasing # of seconds }
      self.fetch_urls_and_save(next_fetch_urls)
    # print "Fetched", self.urls_cnt, "urls"

  def run(self):
    start_time = datetime.now()
    urls = self.get_urls()  # [{domain : { "urls" : [url1, url2, .., urln], "last_fetch" : decreasing # of seconds }}]
    self.fetch_and_save_all(urls)
    c = datetime.now() - start_time
    print "Fetcher took", c

