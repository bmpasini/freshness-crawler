from datetime import datetime
from elasticsearch import Elasticsearch
import sys

class ElasticSearchIndexer(object):
  
  def __init__(self, input_dir, index_name, doc_type):
    self.es = Elasticsearch() # by default we connect to localhost:9200
    self.input_dir = input_dir
    self.index_name = index_name
    self.doc_type = doc_type

  def get_document(self):
    document = {
      'author': 'kimchy',
      'text': 'Elasticsearch: cool. bonsai cool.',
      'timestamp': datetime.now()
    }
    return document

  def document_indexer(self, index_name, doc_type, document):
    res = es.index(index=index_name, doc_type=doc_type, body=document)
    return res

  def document_getter(self, index_name, doc_type, doc_id):
    res = es.index(index=index_name, doc_type=doc_type, id=doc_id)
    return res

  def indices_refresher(self):
    es.indices.refresh(index="test-index")

  def run(self):
    res = self.document_indexer("test-index", 'tweet', self.get_document())
    print res['created'] # indexing
    res = self.document_getter("test-index", 'tweet', 1) # getting
    print res['_source']
    self.indices_refresher()# refresh indices

    # search all
    res = es.search(index="test-index", body={"query": {"match_all": {}}})
    print "Got %d Hits:" % res['hits']['total']
    for hit in res['hits']['hits']:
      print "%(timestamp)s %(author)s: %(text)s" % hit["_source"]

if __name__ == "__main__":
  start_time = datetime.now()
  input_dir = sys.argv[1]
  index_name = sys.argv[2]
  doc_type = sys.argv[3] if sys.argv[3] else 'page' # test this
  elasticSearchIndexer = ElasticSearchIndexer(input_dir, index_name, doc_type)
  elasticSearchIndexer.run()
  c = datetime.now() - start_time
  print "ElasticSearch Indexer took", c, "in total."


