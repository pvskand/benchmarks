#!/bin/bash
#
# Wrapper script to unpack and build shogun.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One shogun*.tar.gz file should be located in this directory.
tars=`ls shogun*.tar.gz | wc -l`;
if [ "$tars" -eq "0" ];
then
  echo "No shogun source .tar.gz found in libraries/!"
  exit 1
fi
if [ "$tars" -ne "1" ];
then
  echo "More than one shogun source .tar.gz found."
  echo "Ensure only one is present in libraries/!"
  exit 1
fi

# Remove any old directory.
rm -rf shogun/
mkdir shogun/
tar -xzpf shogun*.tar.gz --strip-components=1 -C shogun/

cd shogun/
mkdir build/
cd build/
cmake -DPYTHON_INCLUDE_DIR=/usr/include/python3.5 \
    -DPYTHON_EXECUTABLE:FILEPATH=/usr/bin/python3 \
    -DPYTHON_PACKAGES_PATH=../../lib/python3.5/dist-packages \
    -DPythonModular=ON \
    -DBUILD_META_EXAMPLES=OFF \
    -DCMAKE_BUILD_TYPE=Release \
    -DENABLE_TESTING=OFF \
    -DCMAKE_INSTALL_PREFIX=../../ \
    ../
make
make install
