from datetime import datetime
from elasticsearch import Elasticsearch
import sys

class ElasticSearchIndexer(object):
  
  def __init__(self, input_dir, index_name, type_name):
    self.es = Elasticsearch() # by default we connect to localhost:9200
    self.input_dir = input_dir
    self.index_name = index_name
    self.type_name = type_name

  def get_doc(self):
    doc = {
      'author': 'kimchy',
      'text': 'Elasticsearch: cool. bonsai cool.',
      'timestamp': datetime.now()
    }
    return doc

  def run(self):
    # indexing
    res = es.index(index="test-index", doc_type='tweet', id=1, body=doc)
    print res['created']

    # getting
    res = es.get(index="test-index", doc_type='tweet', id=1)
    print res['_source']

    # refresh?
    es.indices.refresh(index="test-index")

    # search all
    res = es.search(index="test-index", body={"query": {"match_all": {}}})
    print "Got %d Hits:" % res['hits']['total']
    for hit in res['hits']['hits']:
      print "%(timestamp)s %(author)s: %(text)s" % hit["_source"]

if __name__ == "__main__":
  start_time = datetime.now()
  input_dir = sys.argv[1]
  index_name = sys.argv[2]
  type_name = sys.argv[3] if sys.argv[3] else 'page' # test this
  elasticSearchIndexer = ElasticSearchIndexer(input_dir, index_name, type_name)
  elasticSearchIndexer.run()
  c = datetime.now() - start_time
  print "ElasticSearch Indexer took", c, "in total."




