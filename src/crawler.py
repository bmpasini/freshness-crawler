import sys
import os
import shutil
from fetcher import Fetcher
from extractor import Extractor
from url_handler import UrlHandler
from scheduler import Scheduler

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
    tmp_dir = "tmp/run_" + str(self.run_number)
    Fetcher(self.url_file, self.run_number).run()
    Extractor(tmp_dir, self.run_number).run()
    UrlHandler(self.run_number).run()
    Scheduler(self.run_number).run()

  def run(self):
    while self.run_number <= self.num_of_runs:
      self.single_run()
      self.run_number += 1

if __name__ == "__main__":
  url_file = sys.argv[1]
  num_of_runs = int(sys.argv[2])
  crawler = Crawler(url_file, num_of_runs)
  crawler.run()

