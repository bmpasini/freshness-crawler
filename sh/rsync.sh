# rsync -avzhe ssh --exclude '.git' --exclude 'tmp' --exclude 'tmp_links' --exclude 'output' --exclude 'log.txt' --exclude 'err.txt' --exclude '.gitignore' --exclude '.DS_Store' --exclude 'notes.txt' --progress /Users/brunomacedo/Desktop/NYU-Poly/3rd-Semester/Memex/code/freshness-crawler bmpasini@gray17.poly.edu:/san_data/research/bmpasini

rsync -avzhe ssh --exclude '.git' --exclude 'tmp' --exclude 'tmp_links' --exclude 'output' --exclude 'log*.txt' --exclude 'err.txt' --exclude '.gitignore' --exclude '.DS_Store' --exclude 'notes.txt' --progress /Users/brunomacedo/Desktop/NYU-Poly/3rd-Semester/Memex/code/freshness-crawler bmpasini@gray17.poly.edu:/san_data/research/bmpasini

# rsync -avzhe ssh --progress bmpasini@vidaserver1.poly.edu:/san_data/research/bmpasini/freshness-crawler/data/20150725152202/log.txt /Users/brunomacedo/Desktop/NYU-Poly/3rd-Semester/Memex/code/freshness-crawler
