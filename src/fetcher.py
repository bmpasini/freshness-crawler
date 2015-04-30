import sys
import os
import urllib

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

  def run(self):
    urls = self.get_urls() # {domain : [url1, url2, .., urln]}
    complete = self.fetch_and_save_all(urls)
    return complete

if __name__ == "__main__":
  url_file = sys.argv[1]
  fetcher = Fetcher(url_file)
  fetcher.run()

