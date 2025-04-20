wget https://exiftool.org/Image-ExifTool-12.87.tar.gz
gzip -dc Image-ExifTool-12.87.tar.gz | tar -xf -
cd Image-ExifTool-12.87
perl Makefile.PL
make install
