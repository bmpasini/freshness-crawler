import os
import urllib2
from bs4 import BeautifulSoup, SoupStrainer
from urlparse import urljoin
import json
# import gevent
# from gevent import monkey
# from gevent.pool import Pool
# from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import copy_reg
import types
import re
from datetime import datetime

# gevent.monkey.patch_all(thread=False)

class Extractor(object):
  
  def __init__(self, dirname, run_number):
    self.dirname = dirname
    self.run_number = run_number
    self.links = []
    self.edges = []

  def get_all_files(self):
    print "Loading all filenames"
    files = []
    for [path, dirnames, filenames] in os.walk(self.dirname):
      for filename in filenames:
        files.append(path + "/" + filename)
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
    if regex.search(url): # test if is well formed
      try:
        url.decode('utf-8') # test if it is unicode
        return True
      except UnicodeError:
        return False
    else:
      return False

  def is_blacklisted(self, url):
    regex = re.compile(r'(\.pdf$)|(\.xls$)|(\.xlsx$)|(\.doc$)|(\.docx$)|(\.ppt$)|(\.pptx$)|(\.rss$)|(\.jpeg$)|(\.mp3$)|(\.mp4$)|(\.wmv$)|(\.jpg$)|(\.png$)|(\.gif$)|(\.exe$)|(\.dmg$)|(\.aac$)|(\.ogg$)|(\.tar$)|(\.tar\.gz$)|(\.tgz$)|(\.avi$)|(\.rmvb$)|(\.xsl$)|(\.jsp$)|(\.plex$)', re.IGNORECASE) # skip urls that end in those extensions
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
    for link in links:
      if link not in self.links:
        self.links.append(link)
      self.edges.append([origin, link, timestamp])

  # def _pickle_method(self, method):
  #   func_name = method.im_func.__name__
  #   obj = method.im_self
  #   cls = method.im_class
  #   return self._unpickle_method, (func_name, obj, cls)

  # def _unpickle_method(self, func_name, obj, cls):
  #   for cls in cls.mro():
  #     try:
  #       func = cls.__dict__[func_name]
  #     except KeyError:
  #       pass
  #     else:
  #       break
  #       return func.__get__(obj, cls)

  def get_edges_from_files(self, files):
    print "Starting extraction number", str(self.run_number)
    # copy_reg.pickle(types.MethodType, self._pickle_method, self._unpickle_method)
    pool = ThreadPool(64)
    pool.map(self.get_edges_from_file, files)
    pool.close()
    pool.join()
    print "Successfully extracted", len(self.links), "new links"
    # pool = Pool(1000)
    # print "Starting extraction number", str(self.run_number)
    # for f in files:
    #   pool.spawn(self.get_edges_from_file, f)
    # pool.join()
    # print "Successfully extracted", len(self.links), "new links"

  def run(self):
    start_time = datetime.now()
    files = self.get_all_files()
    self.get_edges_from_files(files)
    c = datetime.now() - start_time
    print c
    return self.edges # edges stay in memory this way

