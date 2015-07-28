find file_tmp/ -type f -exec perl -e 'print (-B $_ ? "$_\n" : "" ) for @ARGV' {} + > binary.txt &
# xargs rm < binary.txt
# xargs rm < find file_tmp/ -type f -exec perl -e 'print (-B $_ ? "$_\n" : "" ) for @ARGV' {} + &