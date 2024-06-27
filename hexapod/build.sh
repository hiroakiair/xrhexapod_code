#!/bin/sh
set -e
build_dir="./build/"
release_dir="./release/"
if [ ! -d "$build_dir" ]; then
	echo -e "\033[35mcreate build directory\033[0m"
	mkdir ./build
fi
echo -e "\033[35mmake xrtsbase.out\033[0m"
cd cpp
make
echo "\n\033[44;37mAll done, thank you.\033[0m\n"
