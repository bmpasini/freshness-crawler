import sys
import os
import shutil
import json
from datetime import datetime

class JsonToFile(object):

  def __init__(self, input_dirname, output_dirname):
    self.input_dirname = input_dirname
    self.output_dirname = output_dirname

  def get_num_of_runs(self, dirname):
    for [root, dirs, files] in os.walk(dirname):
      num = len(dirs)
      break
    return num

  def get_all_files(self, dirname):
    print "loading all filenames"
    all_files = []
    for [root, dirs, files] in os.walk(dirname):
      for name in files:
        all_files.append(os.path.join(root,name))
    all_files.pop(0)
    print "finished loading filenames"
    return all_files

  def create_diretories(self, path, num):
    self.create_diretory(path)
    for i in range(num):
      n = i + 1
      self.create_diretory(path + "/run_" + str(n))

  def create_diretory(self, path):
    if not os.path.exists(path):
      os.makedirs(path)

  def get_html(self, file_path):
    print file_path
    with open(file_path, 'r') as tmp:
      json_string = " ".join(tmp.readlines())
      try:
        json_dict = json.loads(json_string) if json_string else { "html" : "" }
      except ValueError:
        json_dict = { "html" : "" }
      html = json_dict["html"]
    return html

  def clear_folder(self, path):
    if os.path.exists(path):
      shutil.rmtree(path)

  def save_html(self, html, file_path):
    new_path = file_path.replace('/tmp/', '/file_tmp/')
    root, filename = new_path.rsplit('/', 1)
    self.create_diretory(root)
    with open(new_path, 'w') as tmp:
      tmp.write(html.encode('ascii', 'replace'))

  def save_htmls(self, files, num):
    self.clear_folder(self.output_dirname)
    self.create_diretories(self.output_dirname, num)
    for file_path in files:
      html = self.get_html(file_path)
      self.save_html(html, file_path)

  def run(self):
    print "saving htmls from tmp into file_tmp"
    num = self.get_num_of_runs(self.input_dirname)
    files = self.get_all_files(self.input_dirname)
    self.save_htmls(files, num)

if __name__ == "__main__":
  start_time = datetime.now()
  input_dirname = os.path.join(os.path.realpath(__file__).rsplit('/', 2)[0],'tmp')
  output_dirname = os.path.join(os.path.realpath(__file__).rsplit('/', 2)[0],'file_tmp')
  jsonToFile = JsonToFile(input_dirname, output_dirname)
  jsonToFile.run()
  c = datetime.now() - start_time
  print "JsonToFile took", c

