import sys
import os
import urllib
from bs4 import BeautifulSoup
import csv

# save htmls in memory

class Fetcher(object):

  def __init__(self, url_file):
    self.url_file = url_file

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
        urls[domain] = []
      urls[domain].append(url)
    return urls

  def next_fetch(self, urls):
    fetch_urls = []
    domains_to_remove = []
    for domain in urls: # ordenar dictionary
      fetch_urls.append(urls[domain].pop())
      if urls[domain] == []:
        domains_to_remove.append(domain)
    for domain in domains_to_remove:
      del urls[domain]
    return fetch_urls

  def create_diretory(self, path):
    if not os.path.exists(path):
      os.makedirs(path)

  def save_html(self, url, html):
    self.create_diretory("tmp")
    domain = self.parse_domain(url)
    path = "tmp/" + domain
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
    htmls = {}
    while urls != {}:
      next_fetch_urls = self.next_fetch(urls)
      self.fetch_urls_and_save(htmls, next_fetch_urls)
    print "Fetched", len(htmls), "urls."
    return htmls
    # return True

  def run(self):
    urls = self.get_urls() # {domain : [url1, url2, .., urln]}
    complete = self.fetch_and_save_all(urls)
    return complete


class Extractor(object):
  
  def __init__(self, htmls):
    self.htmls = htmls

  def extract_links(self, html):
    links = []
    soup = BeautifulSoup(html)
    for tag in soup.find_all('a'):
      link = tag.get('href', None)
      link = str(link)
      if "http://" in link:
        links.append(link)
      elif "https://" in link:
        links.append(link)
    return links

  def get_edges_from_html(self, origin, html):
    edges = []
    links = self.extract_links(html)
    for link in links:
      edges.append([origin, link])
    return edges

  def get_edges_from_htmls(self, htmls):
    edges = []
    for url in htmls:
      print "Loading links from", url
      edges += self.get_edges_from_html(url, htmls[url])
    return edges

  def remove_file(self, path):
    if os.path.exists(path):
      os.remove(path)

  def create_diretory(self, path):
    if not os.path.exists(path):
      os.makedirs(path)

  def save_edges(self, edges):
    self.create_diretory("output")
    # outlinks
    edges = [["url", "outlink"]] + edges
    self.remove_file("output/outlinks.csv")
    with open('output/outlinks.csv', 'wb') as fp:
      a = csv.writer(fp, delimiter=',')
      for edge in edges:
        a.writerow(edge)
    # backlinks
    edges[0] = ["url", "backlink"]
    self.remove_file("output/backlinks.csv")
    with open('output/backlinks.csv', 'wb') as fp:
      a = csv.writer(fp, delimiter=',')
      for edge in edges:
        inverted = [edge[1],edge[0]]
        a.writerow(inverted)

  def run(self):
    edges = self.get_edges_from_htmls(self.htmls)
    self.save_edges(edges)

class Crawler(object):

  def __init__(self, url_file):
    self.url_file = url_file

  def wait_fetch(self, htmls):
    while True:
      try:
        htmls
      except NameError:
        pass
      else:
        break

  def run(self):
    fetcher = Fetcher(url_file)
    htmls = fetcher.run()
    self.wait_fetch(htmls)    
    extractor = Extractor(htmls)
    extractor.run()

# if __name__ == "__main__":
#   url_file = sys.argv[1]
#   fetcher = Fetcher(url_file)
#   fetcher.run()

# if __name__ == "__main__":
#   urls_directory = sys.argv[1]
#   extractor = Extractor(urls_directory)
#   extractor.run()

if __name__ == "__main__":
  url_file = sys.argv[1]
  crawler = Crawler(url_file)
  crawler.run()

