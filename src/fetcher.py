import os
import urllib2
from datetime import timedelta
from datetime import datetime
import json
import ssl

TIMEOUT_DOMAIN_FETCH = 0 # seconds

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

  # read response and return whatever is needed in the form of a stringified dictionary
  def read_response(self, response):
    html = response.read()
    # response_dict = { "html" : html }
    headers = response.info().headers
    response_dict = { "html" : unicode(html, "ISO-8859-1"), "headers" : headers, "timestamp" : datetime.now().strftime("%m/%d/%Y %H:%M:%S") }
    return json.dumps(response_dict)

  # def url_fix(s, charset='utf-8'):
  #   if isinstance(s, unicode):
  #     s = s.encode(charset, 'ignore')
  #   scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
  #   path = urllib.quote(path, '/%')
  #   qs = urllib.quote_plus(qs, ':&=')
  #   return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))

  def url_opener(self, url):
    if url[:7] != "http://" and url[:8] != "https://":
      url = "http://" + url
    try:
      return urllib2.urlopen(url)
    except ssl.CertificateError:
      pass

  def fetch_urls_and_save(self, responses, urls):
    for url in urls:
      try:
        # url = url_fix(url)
        response = self.url_opener(url)
        # responses[url] = response.read()
        responses[url] = self.read_response(response)
        print len(responses), ":", url
        self.save_response(url, responses[url])
      except IOError:
        pass
      except AttributeError: # skip https site with invalid ssl certificate
        pass

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

