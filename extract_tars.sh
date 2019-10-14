#!/bin/bash

cd gnu_projects/
files=$(ls)
for f in $files
do
	echo "Extracting $f ..."
	tar -xzf $f & rm $f
done
