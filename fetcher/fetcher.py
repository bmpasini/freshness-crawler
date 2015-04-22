import sys
import os
import urllib

def get_urls_ary(url_file):
  tmp = open(url_file, "r")
  urls = map(lambda x: x.replace("\n", ""), tmp.readlines())
  tmp.close()
  return urls

def find_between(s, first, last):
  try:
    start = s.index(first) + len(first)
    end = s.index(last, start)
    return s[start:end]
  except ValueError:
    return ""

def parse_domain(url):
  if "http://" in url:
    domain = find_between(url, "http://", "/");
  elif "https://":
    domain = find_between(url, "https://", "/");
  else:
    domain = ""
  return domain

def get_urls(url_file):
  urls = {}
  urls_ary = get_urls_ary(url_file)
  for url in urls_ary:
    domain = parse_domain(url)
    if domain not in urls:
      urls[domain] = []
    urls[domain].append(url)
  return urls

def next_fetch(urls):
  fetch_urls = []
  domains_to_remove = []
  for domain in urls:
    fetch_urls.append(urls[domain].pop())
    if urls[domain] == []:
      domains_to_remove.append(domain)
  for domain in domains_to_remove:
    del urls[domain]
  return fetch_urls

def create_diretory(path):
  if not os.path.exists(path):
    os.makedirs(path)

def save_html(url, html):
  create_diretory("output")
  domain = parse_domain(url)
  path = "output/" + domain
  create_diretory(path)
  file_path = path + "/" + urllib.quote(url, '')
  tmp = open(file_path, 'a')
  tmp.write(html)
  tmp.close()

def fetch_urls_and_save(htmls, urls):
  for url in urls:
    response = urllib.urlopen(url)
    try:
      htmls[url] = response.read()
      print len(htmls), ":", url
      save_html(url, htmls[url])
    except:
      pass

def fetch_and_save_all(urls):
  htmls = {}
  while urls != {}:
    next_fetch_urls = next_fetch(urls)
    fetch_urls_and_save(htmls, next_fetch_urls)
  return htmls

if __name__ == "__main__":
  url_file = sys.argv[1]
  urls = get_urls(url_file) # {domain : [url1, url2, .., urln]}
  htmls = fetch_and_save_all(urls)



