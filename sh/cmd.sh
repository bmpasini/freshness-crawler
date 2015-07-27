# java -cp 'lib/*' focusedCrawler.tools.ElasticSearchIndexer \
# --input-dir /san_data/research/bmpasini/ache/freshness-crawler/data/20150722152201/tmp/run_1/ \
# --input-format FILE \
# --output-format ACHE \
# --output-es-url http://http://127.0.0.1:9200 \
# --output-es-index ebola-linkdiscovery \
# --output-es-type page-run-1

# java -cp 'lib/*' focusedCrawler.tools.ElasticSearchIndexer --input-dir /Users/brunomacedo/Desktop/NYU-Poly/3rd-Semester/Memex/code/freshness-crawler/file_tmp/run_1/ --input-format FILE --output-format ACHE --output-es-url http://127.0.0.1:9200 --output-es-index ebola-linkdiscovery --output-es-type page-run-1

java -cp 'lib/*' focusedCrawler.tools.ElasticSearchIndexer --input-dir /san_data/research/bmpasini/freshness-crawler/data/20150722152201/file_tmp/run_1/ --input-format FILE --output-format ACHE --output-es-url http://127.0.0.1:9200 --output-es-index ebola-linkdiscovery-run-1 --output-es-type page

java -cp 'lib/*' focusedCrawler.tools.ElasticSearchIndexer --input-dir /san_data/research/bmpasini/freshness-crawler/data/20150722152201/file_tmp/run_2/ --input-format FILE --output-format ACHE --output-es-url http://127.0.0.1:9200 --output-es-index ebola-linkdiscovery-run-2 --output-es-type page

# rsync -avzhe ssh --progress /Users/brunomacedo/Desktop/NYU-Poly/3rd-Semester/Memex/code/memex/ache-search bmpasini@vidaserver1.poly.edu:/san_data/research/bmpasini

# rsync -avzhe ssh --progress bmpasini@vidaserver1.poly.edu:/san_data/research/bmpasini/freshness-crawler/data/20150722152201/tmp/ .

ache-search - http://ea825b09.ngrok.io/   # http://127.0.0.1:8000
ElasticSearch - http://3910b316.ngrok.io/ # http://127.0.0.1:9200

# curl -XGET 'http://127.0.0.1:9200/ebola-linkdiscovery-run-1/page/_count'
# curl -XDELETE 'http://127.0.0.1:9200/ebola-linkdiscovery-run-2/page/'