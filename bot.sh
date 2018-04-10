#!/usr/bin/env bash

clear && echo && $PWD tree -a --dirsfirst -I ".git|venv" && echo '' && git status && echo ''


