gawk 'BEGIN{FS=","}{print $2}' top-1m.csv > urls-1m.txt
head -100000 urls-1m.txt > urls-100k.txt
head -1000 urls-1m.txt > urls-1k.txt