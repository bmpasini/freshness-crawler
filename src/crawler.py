import sys
import os
import urllib2
from bs4 import BeautifulSoup
import csv
from datetime import timedelta
from datetime import datetime
import json
import shutil

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

  def fetch_urls_and_save(self, responses, urls):
    for url in urls:
      try:
        response = urllib2.urlopen(url)
        # responses[url] = response.read()
        responses[url] = self.read_response(response)
        print len(responses), ":", url
        self.save_response(url, responses[url])
      except IOError:
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


class Extractor(object):
  
  def __init__(self, dirname, run_number):
    self.dirname = dirname
    self.run_number = run_number
    self.links = []

  def get_all_files(self):
    print "Loading all filenames"
    files = []
    for [path, dirnames, filenames] in os.walk(self.dirname):
      for filename in filenames:
        files.append(path + "/" + filename)
    files.pop(0)
    print "Done loading", len(files), "filenames"
    return files

  def extract_links(self, html):
    links = []
    soup = BeautifulSoup(html)
    for tag in soup.find_all('a'):
      try:
        link = tag.get('href', None)
        link = str(link)
        if link not in links: # do not include repeated links
          if "http://" in link:
            links.append(link)
          elif "https://" in link:
            links.append(link)
      except UnicodeEncodeError:
        pass
    return links

  def get_html_from_file(self, f):
    tmp = open(f, "r")
    response_str = " ".join(tmp.readlines())
    response_dict = json.loads(response_str)
    html = response_dict["html"]
    timestamp = response_dict["timestamp"]
    tmp.close
    return html, timestamp

  def get_edges_from_file(self, f):
    edges = []
    html, timestamp = self.get_html_from_file(f)
    origin = urllib2.unquote(os.path.basename(os.path.normpath(f)))
    links = self.extract_links(html)
    for link in links:
      if link not in self.links:
        self.links.append(link)
      edges.append([origin, link, timestamp])
    return edges

  def get_edges_from_files(self, files):
    edges = []
    print "Starting extraction number", str(self.run_number)
    for f in files:
      print "Extracting links from", urllib2.unquote(os.path.basename(os.path.normpath(f)))
      edges += self.get_edges_from_file(f)
    print "Successfully extracted", len(self.links), "new links."
    return edges

  def run(self):
    files = self.get_all_files()
    edges = self.get_edges_from_files(files)
    return edges # edges stay in memory this way


class UrlHandler(object):

  def __init__(self, edges, run_number):
    self.edges = edges
    self.run_number = run_number

  def remove_file(self, path):
    if os.path.exists(path):
      os.remove(path)

  def create_diretory(self, path):
    if not os.path.exists(path):
      os.makedirs(path)

  def save_outlinks(self):
    edges = [["url", "outlink"]] + self.edges
    outlink_file = "output/run_" + str(self.run_number) + "/outlinks.csv"
    self.remove_file(outlink_file)
    with open(outlink_file, 'wb') as fp:
      a = csv.writer(fp, delimiter=',', quotechar='"')
      for edge in edges:
        a.writerow(edge[:-1])

  def load_urls_file(self):
    urls = {}
    file_name = "output/urls.csv"
    if not os.path.exists(file_name):
      file(file_name, 'w').close()
    with open(file_name, 'r') as fp:
      csv_reader = csv.reader(fp, delimiter=',', quotechar='"')
      if os.path.getsize(file_name):
        for row in csv_reader:
          urls[row[0]] = [row[1], row[2], row[3]]
    return urls

  def prepare_urls(self): # review this
    urls = self.load_urls_file()
    for edge in self.edges:
      # if edge[0] in urls: # what if an outlink points to a page that has already been crawled? Here, I'm just ignoring...
      #   if urls[edge[0]][0] == 1:
      #     continue
      urls[edge[0]] = [1,self.run_number,edge[2]]
      print urls[edge[0]]
      if edge[1] not in urls:
        urls[edge[1]] = [0,None,None]
        print urls[edge[1]]
    return urls

  def save_urls(self):
    urls = self.prepare_urls() # {url : [fetched?, run_number]}
    file_name = "output/urls.csv"
    with open(file_name, 'w+') as fp:
      a = csv.writer(fp, delimiter=',', quotechar='"')
      for url in sorted(urls):
        row = [url] + urls[url]
        a.writerow(row)

  def run(self):
    self.create_diretory("output")
    self.create_diretory("output/run_" + str(self.run_number))
    self.save_outlinks()
    self.save_urls()


class Scheduler(object):

  def __init__(self, num_of_runs):
    self.url_file = "output/urls.csv"
    self.run_number = 1
    self.num_of_runs = num_of_runs

  def remove_file(self, path):
    if os.path.exists(path):
      os.remove(path)

  def get_urls(self):
    urls = []
    file_name = "output/urls.csv"
    with open(file_name, 'r') as fp:
      csv_reader = csv.reader(fp, delimiter=',', quotechar='"')
      for row in csv_reader:
        url = row[0]
        been_crawled = row[1]
        if been_crawled == "0":
          urls.append(url)
    return urls

  def save_urls(self):
    urls = self.get_urls()
    file_name = "output/run_" + str(self.run_number) + "/urls.txt" 
    self.remove_file(file_name)
    with open(file_name, "a+") as fp:
      for url in set(urls):
        fp.write(url + "\n")

  def run(self):
    self.save_urls()


class Crawler(object):

  def __init__(self, url_file, num_of_runs):
    self.url_file = url_file
    self.run_number = 1
    self.num_of_runs = num_of_runs

  def clear_folder(self, path):
    if os.path.exists(path):
      shutil.rmtree(path)

  def prepare_files(self):
    if self.run_number != 1:
      self.url_file = "output/run_" + str(self.run_number - 1) + "/urls.txt" 
    else:
      self.clear_folder("tmp")
      self.clear_folder("output")

  def single_run(self):
    self.prepare_files()
    fetcher = Fetcher(self.url_file, self.run_number)
    fetcher.run()
    tmp_dir = "tmp/run_" + str(self.run_number)
    extractor = Extractor(tmp_dir, self.run_number)
    edges = extractor.run()
    url_handler = UrlHandler(edges, self.run_number)
    url_handler.run()
    scheduler = Scheduler(self.run_number)
    scheduler.run()

  def run(self):
    while self.run_number <= self.num_of_runs:
      self.single_run()
      self.run_number += 1

if __name__ == "__main__":
  url_file = sys.argv[1]
  num_of_runs = int(sys.argv[2])
  crawler = Crawler(url_file, num_of_runs)
  crawler.run()

