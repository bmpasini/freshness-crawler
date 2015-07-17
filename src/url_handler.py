import os
import csv
import shutil
from datetime import datetime

class UrlHandler(object):

  def __init__(self, run_number):
    self.edges = []
    self.run_number = run_number

  def get_all_files(self, dirname, pop=True):
    print "Loading all filenames"
    files = []
    for [path, dirnames, filenames] in os.walk(dirname):
      for filename in filenames:
        files.append(path + "/" + filename)
    if pop:
      files.pop(0)
    print "Done loading", len(files), "filenames"
    return files

  def prepare_urls_and_save_outlinks(self): # process tmp_links files
    print "Starting tmp_links processing"
    dirname = 'tmp_links'
    links_files = self.get_all_files(dirname, False)
    urls = self.load_urls_file()
    self.create_outlinks_csv()
    outlink_file = "output/run_" + str(self.run_number) + "/outlinks.csv"
    cnt = 0
    with open(outlink_file, 'a') as outlink_fp:
      outlink_writer = csv.writer(outlink_fp, delimiter=',', quotechar='"')
      for links_file in links_files:
        print 'Bringing', links_file, 'into memory'
        with open(links_file, 'r') as links_fp:
          links_reader = csv.reader(links_fp, delimiter=',', quotechar='"')
          if os.path.getsize(links_file):
            for edge in links_reader:
              cnt += 1
              outlink_writer.writerow(edge[:-1]) # write outlink
              # if edge[0] in urls: # what if an outlink points to a page that has already been crawled?
              #   if urls[edge[0]][0] == 1:
              #     continue
              urls[edge[0]] = [1,self.run_number,edge[2]]
              if edge[1] not in urls:
                urls[edge[1]] = [0,None,None]
        self.remove_file(links_file)
    self.clear_folder(dirname)
    print cnt, "links were extracted"
    return urls # {url : [fetched?, run_number, timestamp]}

  def remove_file(self, path):
    if os.path.exists(path):
      os.remove(path)

  def clear_folder(self, path):
    if os.path.exists(path):
      shutil.rmtree(path)

  def create_diretory(self, path):
    if not os.path.exists(path):
      os.makedirs(path)

  def create_outlinks_csv(self):
    edges = [["url", "outlink"]] + self.edges
    outlink_file = "output/run_" + str(self.run_number) + "/outlinks.csv"
    self.remove_file(outlink_file)
    with open(outlink_file, 'w+') as outlink_fp:
      a = csv.writer(outlink_fp, delimiter=',', quotechar='"')
      a.writerow(["url", "outlink"])

  # def save_outlinks(self):
  #   outlink_file = "output/run_" + str(self.run_number) + "/outlinks.csv"
  #   with open(outlink_file, 'a') as outlink_fp:
  #     a = csv.writer(outlink_fp, delimiter=',', quotechar='"')
  #     for edge in edges:
  #       a.writerow(edge[:-1])

  def load_urls_file(self):
    urls = {}
    urls_file = "output/urls.csv"
    if not os.path.exists(urls_file):
      file(urls_file, 'w').close()
    with open(urls_file, 'r') as urls_fp:
      csv_reader = csv.reader(urls_fp, delimiter=',', quotechar='"')
      if os.path.getsize(urls_file):
        for row in csv_reader:
          urls[row[0]] = [row[1], row[2], row[3]]
    return urls

  def save_urls(self):
    print "Starting url handling number", self.run_number
    urls = self.prepare_urls_and_save_outlinks() # {url : [fetched?, run_number, timestamp]}
    urls_file = "output/urls.csv"
    with open(urls_file, 'w+') as urls_fp:
      a = csv.writer(urls_fp, delimiter=',', quotechar='"')
      for url in sorted(urls):
        row = [url] + urls[url]
        a.writerow(row)

  def run(self):
    start_time = datetime.now()
    self.create_diretory("output")
    self.create_diretory("output/run_" + str(self.run_number))
    self.save_urls()
    c = datetime.now() - start_time
    print "UrlHandler took", c

