import os
import urllib2
from bs4 import BeautifulSoup, SoupStrainer
from urlparse import urljoin
import json

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

  def extract_links(self, html, url):
    links = []
    soup = BeautifulSoup(html, parse_only=SoupStrainer('a'))
    for tag in soup.find_all('a'):
      try:
        link = tag.get('href', None)
        link = str(link)
        if link:
            link = link[:-1] if link[-1] == "/" else link # remove '/' from end of url (in order to avoid duplicate urls)
        if link not in links: # do not include repeated links
          if link[:7] == "http://":
            links.append(link)
          elif link[:8] == "https://":
            links.append(link)
          elif link != 'None' and link != '#' and 'javascript' not in link:
            link = urljoin(url, link)
            if link not in links:
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
    links = self.extract_links(html, origin)
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

