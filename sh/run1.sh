DATETIME=$(date +"%Y%m%d%H%M%S")
echo "Make dir $DATETIME ...."
mkdir -p data/$DATETIME && cd data/$DATETIME
cp -r ../../input ../../src ../../sh .
echo "Start crawler "$1" ...."
python src/crawler.py input/urlsComplete.txt 1 > log.txt 2>&1
echo "Task finished at: $(date)" >> log.txt
cd ../..