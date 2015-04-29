import sys
import os
import urllib
from bs4 import BeautifulSoup
import csv

class Extractor(object):
  
  def __init__(self, dirname):
    self.dirname = dirname

  def get_all_files(self):
    print "Loading all filenames"
    files = []
    for [path, dirnames, filenames] in os.walk(self.dirname):
      for filename in filenames:
        files.append(path + "/" + filename)
    files.pop(0)
    print "Done loading filenames", len(files)
    return files

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

  def get_edges_from_file(self, f):
    edges = []
    tmp = open(f, "r")
    html = " ".join(tmp.readlines())
    tmp.close
    origin = urllib.unquote(os.path.basename(os.path.normpath(f)))
    links = self.extract_links(html)
    for link in links:
      edges.append([origin, link])
    return edges

  def get_edges_from_files(self, files):
    edges = []
    for f in files:
      print "Loading links from", urllib.unquote(os.path.basename(os.path.normpath(f)))
      edges += self.get_edges_from_file(f)
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
    files = self.get_all_files()
    edges = self.get_edges_from_files(files)
    self.save_edges(edges)

if __name__ == "__main__":
  urls_directory = sys.argv[1]
  extractor = Extractor(urls_directory)
  extractor.run()


