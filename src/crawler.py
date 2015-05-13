import sys
import os
import urllib
from bs4 import BeautifulSoup
import csv
from datetime import timedelta
from datetime import datetime

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

  def save_html(self, url, html):
    self.create_diretory("tmp")
    tmp_dir = "tmp/run_" + str(self.run_number)
    self.create_diretory(tmp_dir)
    domain = self.parse_domain(url)
    path = tmp_dir + "/" + domain
    self.create_diretory(path)
    file_path = path + "/" + urllib.quote(url, '')
    tmp = open(file_path, 'a')
    tmp.write(html)
    tmp.close()

  def fetch_urls_and_save(self, htmls, urls):
    for url in urls:
      try:
        response = urllib.urlopen(url)
        htmls[url] = response.read()
        print len(htmls), ":", url
        self.save_html(url, htmls[url])
      except IOError:
        pass

  def fetch_and_save_all(self, urls):
    print "Starting fetch number", str(self.run_number)
    htmls = {}
    while urls != {}:
      next_fetch_urls = self.next_fetch(urls) # { "urls" : [url1, url2, .., urln], "last_fetch" : decreasing # of seconds }
      self.fetch_urls_and_save(htmls, next_fetch_urls)
    print "Fetched", len(htmls), "urls."

  def run(self):
    urls = self.get_urls()  # [{domain : { "urls" : [url1, url2, .., urln], "last_fetch" : decreasing # of seconds }}]
    self.fetch_and_save_all(urls)


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

  def get_edges_from_file(self, f):
    edges = []
    tmp = open(f, "r")
    html = " ".join(tmp.readlines())
    tmp.close
    origin = urllib.unquote(os.path.basename(os.path.normpath(f)))
    links = self.extract_links(html)
    for link in links:
      if link not in self.links:
        self.links.append(link)
      edges.append([origin, link])
    return edges

  def get_edges_from_files(self, files):
    edges = []
    print "Starting extraction number", str(self.run_number)
    for f in files:
      print "Extracting links from", urllib.unquote(os.path.basename(os.path.normpath(f)))
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
        a.writerow(edge)

  def get_links(self):
    links = []
    for edge in self.edges:
      links.append(edge[1])
    return links

  def save_links(self):
    links = self.get_links()
    file_name = "output/run_" + str(self.run_number) + "/urls.txt" 
    self.remove_file(file_name)
    with open(file_name, "a+") as fp:
      for link in set(links):
        fp.write(link + "\n")

  def load_urls_file(self):
    urls = {}
    file_name = "output/urls.csv"
    if not os.path.exists(file_name):
      file(file_name, 'w').close()
    with open(file_name, 'wb') as fp:
      csv_reader = csv.reader(fp, delimiter=',', quotechar='"')
      if os.path.getsize(file_name):
        for row in csv_reader:
          urls[row[0]] = [row[1], row[2]]
    return urls

  def prepare_urls(self):
    urls = self.load_urls_file()
    for edge in self.edges:
      urls[edge[0]] = [1,self.run_number]
      if edge[1] not in urls:
        urls[edge[1]] = [0,None]
    return urls

  def save_urls(self):
    urls = self.prepare_urls()
    file_name = "output/urls.csv"
    with open(file_name, 'wb') as fp:
      a = csv.writer(fp, delimiter=',', quotechar='"')
      for domain in urls:
        row = [domain] + urls[domain]
        a.writerow(row)

  def run(self):
    self.create_diretory("output")
    self.create_diretory("output/run_" + str(self.run_number))
    self.save_outlinks()
    self.save_links()
    self.save_urls()


class Crawler(object):

  def __init__(self, url_file, num_of_runs):
    self.url_file = url_file
    self.run_number = 1
    self.num_of_runs = num_of_runs

  def single_run(self):
    if self.run_number != 1:
      self.url_file = "output/run_" + str(self.run_number - 1) + "/urls.txt" 
    fetcher = Fetcher(self.url_file, self.run_number)
    fetcher.run()
    tmp_dir = "tmp/run_" + str(self.run_number)
    extractor = Extractor(tmp_dir, self.run_number)
    edges = extractor.run()
    url_handler = UrlHandler(edges, self.run_number)
    url_handler.run()
    
  def run(self):
    while self.run_number <= self.num_of_runs:
      self.single_run()
      self.run_number += 1

if __name__ == "__main__":
  url_file = sys.argv[1]
  num_of_runs = int(sys.argv[2])
  crawler = Crawler(url_file, num_of_runs)
  crawler.run()

