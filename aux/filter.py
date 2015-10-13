import sys
import os
import shutil
import json
from datetime import datetime

class Filter(object):

  def __init__(self, input_dirname, output_dirname):
    self.input_dirname = input_dirname
    self.output_dirname = output_dirname

  def get_all_files(self, dirname):
    print "loading all filenames"
    all_files = []
    for [root, dirs, files] in os.walk(dirname):
      if root != self.input_dirname:
        for name in files:
          all_files.append(os.path.join(root,name))
    print len(all_files)
    print "finished loading filenames"
    return all_files

  def clear_folder(self, path):
    if os.path.exists(path):
      shutil.rmtree(path)

  def create_diretory(self, path):
    if not os.path.exists(path):
      os.makedirs(path)

  def get_url_and_status_code(self, file_path):
    # print file_path
    with open(file_path, 'r') as tmp:
      json_string = " ".join(tmp.readlines())
      try:
        if json_string:
          json_dict = json.loads(json_string)
        else:
          json_dict = { "url" : "", "status_code" : "" }
      except ValueError:
        json_dict = { "url" : "", "status_code" : "" }
      url = json_dict["url"]
      status_code = json_dict["status_code"]
    return [ url, status_code ]

  def save_200_urls(self, files):
    i = 0
    j = 0
    z = 0
    file_path = os.path.join(output_dirname, 'moviesNegative.clean')
    clean_urls = []
    with open(file_path, 'w+') as tmp:
      for f in files:
        print self.get_url_and_status_code(f)
        url, status_code = self.get_url_and_status_code(f)
        if status_code == 200:
          if url in clean_urls:
            j += 1
          else:
            tmp.write(url + '\n')
          clean_urls.append(url)
          i += 1
        else:
          z += 1
    print i, "urls have 200 status,", j, "of them are repeated.", z, "urls were discarded, because they are not 200."
    print "Final total of urls:", i - j

  def run(self):
    print "saving htmls from tmp into file_tmp"
    files = self.get_all_files(self.input_dirname)
    self.save_200_urls(files)

if __name__ == "__main__":
  start_time = datetime.now()
  input_dirname = os.path.join(os.path.realpath(__file__).rsplit('/', 2)[0],'tmp_movies_negative/run_1')
  output_dirname = os.path.join(os.path.realpath(__file__).rsplit('/', 2)[0],'seeds/movies/')
  filter = Filter(input_dirname, output_dirname)
  filter.run()
  c = datetime.now() - start_time
  print "Filter took", c

