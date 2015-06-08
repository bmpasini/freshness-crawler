echo "Make dir "$(date +"%Y%m%d%H%M%S")" ...."
mkdir -p data/$(date +"%Y%m%d%H%M%S") && cd data/$(date +"%Y%m%d%H%M%S")
cp -r ../../input ../../src ../../sh .
echo "Start crawler "$1" ...."
# python src/crawler.py input/ebola_urls-100.txt 3 > log.out 2> log.err < /dev/null &
# python src/crawler.py input/ebola_urls-100.txt 3 > log.out 2>&1 < /dev/null &
# python src/crawler.py input/ebola_urls-100.txt 3 > log.txt &
python src/crawler.py input/urlsComplete.txt 2 > log.txt 2> err.txt < /dev/null &
cd ../..