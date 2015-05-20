echo "Start crawler "$1" ...."
# nohup python src/crawler.py input/urls-100k.txt 1 > log.out 2> log.err < /dev/null &
# nohup python src/crawler.py input/urls-100k.txt 1 > log.out 2>&1 < /dev/null &
python src/crawler.py input/urls-100k.txt 1