import os
import csv
from datetime import datetime

class Scheduler(object):

  def __init__(self, run_number):
    self.url_file = "output/urls.csv"
    self.run_number = run_number

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
    print len(urls), "new links scheduled for the next run"
    return urls

  def save_urls(self):
    print "Starting scheduler number", self.run_number
    urls = self.get_urls()
    file_name = "output/run_" + str(self.run_number) + "/urls.txt" 
    self.remove_file(file_name)
    with open(file_name, 'a') as fp:
      for url in sorted(set(urls)):
        fp.write(url + "\n")

  def run(self):
    start_time = datetime.now()
    self.save_urls()
    c = datetime.now() - start_time
    print "Scheduler took", c