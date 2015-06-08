import sys
import urllib2

lines = []
f = sys.argv[1]
with open(f, "r") as tmp:
  for line in tmp:
    lines.append(urllib2.unquote(line))

with open(f, "w+") as tmp:
  for line in lines:
    tmp.write(line)