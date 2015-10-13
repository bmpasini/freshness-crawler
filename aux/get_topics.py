import sys
import re
from random import randint

RDF = "../../../aux/content.rdf.u8"
START = re.compile("<Topic r:id=\"(.*)\">")
END = re.compile("</Topic>")
LINK = re.compile("<link r:resource=\"(.*)\"></link>")

def get_links(output):
  links = []
  inTopic = False
  rightTopic = False
  count = 0
  topic = ""
  topics = set()
  with open(RDF) as lines:
    for line in lines:
      count += 1
      if (count % 1000000) == 0:
        print "Processing..." + str(count)
      if inTopic:
        END_match = END.search(line)
        if END_match:
          inTopic = False
          rightTopic = False
        else:
          if rightTopic:
            LINK_match = LINK.search(line)
            if topic in topics:
              continue
            if LINK_match:
               isContinue = False
               for ex_topic in EXCLUSIVE_TOPICS:
                 if ex_topic in topic:
                   isContinue = True
               if isContinue == True:
                 continue
               else:
                 output.write(LINK_match.group(1) + "\t" + topic + "\n")
                 topics.add(topic)
      else:
        START_match = START.search(line)
        if START_match:
          inTopic = True
          topic = START_match.group(1)
          for in_topic in INCLUSIVE_TOPICS:
            if in_topic in topic:
              rightTopic = True #Scan right topics

def main(argv):
  output_file = open(argv, "w")
  get_links(output_file)
  output_file.close()

if __name__=="__main__":
  output_dir = "/Users/brunomacedo/Desktop/NYU-Poly/3rd-Semester/Memex/code/freshness-crawler/seeds/ebola/negative_candidates/"

  INCLUSIVE_TOPICS = ["Health/Conditions_and_Diseases/Infectious_Diseases/Viral/Hemorrhagic_Fevers/"]
  EXCLUSIVE_TOPICS = ["Ebola"]
  topic = "health-diseases-infectious-viral-fever"
  print topic
  main(output_dir + topic)

  INCLUSIVE_TOPICS = ["Health/Conditions_and_Diseases/Infectious_Diseases/Viral/"]
  EXCLUSIVE_TOPICS = ["Hemorrhagic_Fevers"]
  topic = "health-diseases-infectious-viral"
  print topic
  main(output_dir + topic)

  INCLUSIVE_TOPICS = ["Health/Conditions_and_Diseases/Infectious_Diseases/"]
  EXCLUSIVE_TOPICS = ["Viral"]
  topic = "health-diseases-infectious"
  print topic
  main(output_dir + topic)

  INCLUSIVE_TOPICS = ["Health/Conditions_and_Diseases/"]
  EXCLUSIVE_TOPICS = ["Infectious_Diseases"]
  topic = "health-diseases"
  print topic
  main(output_dir + topic)

  INCLUSIVE_TOPICS = ["Health/"]
  EXCLUSIVE_TOPICS = ["Conditions_and_Diseases"]
  topic = "health"
  print topic
  main(output_dir + topic)

  # main(sys.argv[1:])
