import os
import csv

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
      if edge[1] not in urls:
        urls[edge[1]] = [0,None,None]
    return urls

  def save_urls(self):
    print "Handling new urls"
    urls = self.prepare_urls() # {url : [fetched?, run_number, timestamp]}
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

