DATETIME=$(date +"%Y%m%d%H%M%S")
CRAWLER_PATH=/san_data/research/bmpasini/freshness-crawler

# create directory whose name is the date and time the job started
mkdir -p $CRAWLER_PATH/data/$DATETIME && cd $CRAWLER_PATH/data/$DATETIME
echo "Make directory data/$DATETIME ...." >> $CRAWLER_PATH/data/$DATETIME/log.txt

# copy the source files and input files to that directory
echo "Copy files to directory data/$DATETIME ...." >> $CRAWLER_PATH/data/$DATETIME/log.txt
cp -r $CRAWLER_PATH/input $CRAWLER_PATH/src $CRAWLER_PATH/sh $CRAWLER_PATH/data/$DATETIME

# run crawler
echo "Start crawler "$1" ...." >> $CRAWLER_PATH/data/$DATETIME/log.txt
python -u -W all -vv $CRAWLER_PATH/data/$DATETIME/src/crawler.py $CRAWLER_PATH/data/$DATETIME/input/ebolaSeeds.txt 2 >> $CRAWLER_PATH/data/$DATETIME/log.txt 2>&1

# print datetime when job finished
echo "Task finished at: $(date)" >> $CRAWLER_PATH/data/$DATETIME/log.txt