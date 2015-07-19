from lsapi import lsapi
from lsapi import lsapiException
import time

# input: file with a list of seed urls
# output: file with a list of seed urls + backlinks

MOZ = { 'access_id': 'mozscape-d7201e2b23', 'secret_key': 'd605753f7d3a2f970353754a4b123b4c' }
l = lsapi(MOZ['access_id'], MOZ['secret_key'])
seeds_path = 'input/ebola-1000.txt'
result_path = 'input/ebolaSeeds-3.txt'

if __name__ == "__main__":

  print "Start backlink fetcher"
  
  with open(seeds_path, 'r') as seeds_fp:
    seeds = map(lambda x: x.replace("\n", ""), seeds_fp.readlines())

  backlinks_dict = {}
  cnt = 0

  # go through seeds, get backlinks from each and put in a dict[seed] = [backlinks]
  for seed in seeds:
    cnt += 1
    seed_backlinks = []
    try:
      links = l.links(seed, scope='page_to_page', sort='page_authority', filters=['external'], targetCols = lsapi.UMCols.url)
    except lsapiException, e:
      links = []
      print "lsapiException:", e
    for link in links:
      seed_backlinks.append(link['uu'])
    backlinks_dict[seed] = seed_backlinks
    print cnt, ": {", seed, ":", backlinks_dict[seed], "}"
    time.sleep(10)

  with open(result_path, 'w') as fp:
    for seed in backlinks_dict:
      fp.write(seed + "\n")
      for backlink in backlinks_dict[seed]:
        fp.write(backlink + "\n")

  print "File writing complete"

# https://moz.com/help/guides/moz-api/mozscape/api-reference/response-fields
# https://moz.com/researchtools/ose/links?site=www.seomoz.org&filter=&source=all&target=page&group=0&page=1&sort=page_authority&anchor_id=&anchor_type=&anchor_text=&from_site=