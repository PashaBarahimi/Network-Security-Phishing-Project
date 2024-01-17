#!/usr/bin/env bash

go install github.com/imthaghost/goclone/cmd/goclone@latest
goclone $1 # $1 is the url of the website you want to clone
url=$(echo $1 | cut -d'/' -f3)
mv $url static

python3 main.py "0.0.0.0" 8080
