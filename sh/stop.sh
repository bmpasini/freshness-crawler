echo "Shut down crawler "$1" ...."
kill -9 $(ps aux | grep crawler | grep -v "grep" | awk '{print $2}')