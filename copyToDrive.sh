#!/bin/bash

echo "Rsync"
rsync -a --delete --exclude ".*" ./ /Volumes/PROGGERCODE/

echo "Done"