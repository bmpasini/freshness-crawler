DATETIME=$(date +"%Y%m%d%H%M%S")

# create directory whose name is the date and time the job started
mkdir -p /san_data/research/bmpasini/freshness-crawler/data/$DATETIME && cd /san_data/research/bmpasini/freshness-crawler/data/$DATETIME
echo "Make directory data/$DATETIME ...." >> /san_data/research/bmpasini/freshness-crawler/data/$DATETIME/log.txt

# copy the source files and input files to that directory
echo "Copy files to directory data/$DATETIME ...." >> /san_data/research/bmpasini/freshness-crawler/data/$DATETIME/log.txt
cp -r /san_data/research/bmpasini/freshness-crawler/input /san_data/research/bmpasini/freshness-crawler/src /san_data/research/bmpasini/freshness-crawler/sh /san_data/research/bmpasini/freshness-crawler/data/$DATETIME

# run crawler
echo "Start crawler "$1" ...." >> /san_data/research/bmpasini/freshness-crawler/data/$DATETIME/log.txt
time -a -o /san_data/research/bmpasini/freshness-crawler/data/$DATETIME/log.txt python -u /san_data/research/bmpasini/freshness-crawler/data/$DATETIME/src/crawler.py /san_data/research/bmpasini/freshness-crawler/data/$DATETIME/input/urlsComplete.txt 3 >> /san_data/research/bmpasini/freshness-crawler/data/$DATETIME/log.txt 2>&1

# print datetime when job finished
echo "Task finished at: $(date)" >> /san_data/research/bmpasini/freshness-crawler/data/$DATETIME/log.txt