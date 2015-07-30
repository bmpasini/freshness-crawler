import os
import urllib2
from bs4 import BeautifulSoup, SoupStrainer
from urlparse import urljoin
import json
from multiprocessing import Process, current_process
import copy_reg
import types
import re
from datetime import datetime
import csv
import shutil
import multiprocessing

NUMBER_OF_CORES = multiprocessing.cpu_count()

class Extractor(object):
  
  def __init__(self, dirname, run_number):
    self.dirname = dirname
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

  def url_is_well_formed(self, url):
    regex = re.compile(
            r'^(?:http)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
            r'localhost|' # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if regex.search(url): # test if it is well formed
      try:
        url.decode('utf-8') # test if it is unicode
        return True
      except UnicodeError:
        return False
    else:
      return False

  def is_blacklisted(self, url):
    regex = re.compile(r'(\.pdf$)|(\.xls$)|(\.xlsx$)|(\.doc$)|(\.docx$)|(\.ppt$)|(\.pptx$)|(\.rss$)|(\.jpeg$)|(\.mp3$)|(\.mp4$)|(\.wmv$)|(\.jpg$)|(\.png$)|(\.gif$)|(\.exe$)|(\.dmg$)|(\.aac$)|(\.ogg$)|(\.tar$)|(\.tar\.gz$)|(\.tgz$)|(\.avi$)|(\.rmvb$)|(\.xsl$)|(\.jsp$)|(\.plex$)|(\.tiff$)|(\.img$)|(\.zip$)|(\.bmp$)|(\.mov$)|(\.wav$)|(\.webm$)|(\.ogv$)|(\.swf$)|(\.oga$)|(\.ico$)|(\.cfm$)', re.IGNORECASE) # skip urls that end in these extensions
    if regex.search(url): # test if is blacklisted
      return True
    else:
      return False

  def clean_link(self, link, url):
    try:
      link = str(link)
      if link:
        if link[:7] != "http://" and link[:8] != "https://": # if relative path, join with url domain
          link = urljoin(url, link)
        link = link[:-1] if link[-1] == "/" else link # remove '/' from end of url (in order to avoid duplicate urls)
        link = link.split('#', 1)[0] # remove everything after '#'
        link = link.replace('&amp', '&') # replace &amp with &
        if self.is_blacklisted(link): # skip blacklisted urls
          return None
        else:
          if self.url_is_well_formed(link):
            return link
          else:
            return None
      else:
        return None
    except UnicodeEncodeError:
      return None

  def extract_links(self, html, url):
    print "Extracting links from", url
    links = []
    soup = BeautifulSoup(html, parse_only=SoupStrainer('a'))
    for tag in soup.find_all('a'):
      link = tag.get('href', None)
      link = self.clean_link(link, url)
      if link not in links and link != None: # do not include repeated links
        links.append(link)
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
    html, timestamp = self.get_html_from_file(f)
    origin = urllib2.unquote(os.path.basename(os.path.normpath(f)))
    links = self.extract_links(html, origin)
    proc_name = current_process().name
    self.save_links_temporarily(origin, links, timestamp, proc_name)

  def save_links_temporarily(self, origin, links, timestamp, proc_name):
    file_path = 'tmp_links/' + proc_name
    with open(file_path, 'a+') as fp:
      a = csv.writer(fp, delimiter=',', quotechar='"')
      for link in links:
        a.writerow([origin, link, timestamp])

  def create_diretory(self, path):
    if not os.path.exists(path):
      os.makedirs(path)

  def get_edges_from_files_chunk(self, files):
    for f in files:
      self.get_edges_from_file(f)

  def file_splitter(self, files, cores=NUMBER_OF_CORES):
    files_chunk = [[] for x in range(cores)]
    while files:
      for i in range(cores):
        if files:
          files_chunk[i].append(files.pop(0))
    return files_chunk

  def get_edges_from_files(self, files):
    print "Starting extraction number", str(self.run_number)
    self.create_diretory('tmp_links')
    files = self.file_splitter(files) # split files in 64 chunks
    jobs = []
    for files_chunk in files:
      j = Process(target=self.get_edges_from_files_chunk, args=(files_chunk,))
      jobs.append(j)
      j.start()
    for j in jobs:
      j.join()

  def remove_file(self, path): 
    if os.path.exists(path):
      os.remove(path)

  def clear_folder(self, path):
    if os.path.exists(path):
      shutil.rmtree(path)

  # def bring_temporary_files_into_memory(self):
  #   print "Bringing temporary files into memory"
  #   edges = []
  #   dirname = 'tmp_links'
  #   files = self.get_all_files(dirname, False)
  #   for f in files:
  #     print 'Bringing', f, 'into memory'
  #     with open(f, 'r') as fp:
  #       csv_reader = csv.reader(fp, delimiter=',', quotechar='"')
  #       if os.path.getsize(f):
  #         for edge in csv_reader:
  #           edges.append(edge)
  #     self.remove_file(f)
  #   self.clear_folder(dirname)
  #   print "Successfully extracted", len(edges), "links"
  #   return edges

  def run(self):
    start_time = datetime.now()
    files = self.get_all_files(self.dirname)
    self.get_edges_from_files(files)
    # edges = self.bring_temporary_files_into_memory()
    c = datetime.now() - start_time
    print "Extractor took", c
    # return edges # edges stay in memory this way
