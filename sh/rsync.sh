rsync -avzhe ssh --exclude '.git' --exclude 'tmp' --exclude 'output' --exclude 'log.txt' --exclude 'err.txt' --progress /Users/brunomacedo/Desktop/NYU-Poly/3rd-Semester/Memex/code/freshness-crawler bmpasini@vidaserver1.poly.edu:/san_data/research/bmpasini