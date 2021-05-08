#!/bin/bash

# =================================================
# Variables
# =================================================
silent=0
tmpFile=/tmp/$(basename $0).$$
#dir=~/projects/reportchangelog/repos

# =================================================
# Functions
# =================================================
function help() {
  cat<<EOF
NAME
       `basename $0` - SUMMARY

SYNOPSIS
       `basename $0` [-s] [-h] [-d dir]

DESCRIPTION
       INFO

       -s
              Silent mode

       -h
              Show this help

       -d     
              Folder where repos are clonned (def: $dir)
EOF
}

function trace() {
  [ $silent -eq 0 ] && echo $* >&2
}

# =================================================
# Arguments
# =================================================
while getopts "hsd:" opt
do
  case $opt in
    h)
      help
      exit 0
      ;;
    s) silent=1 ;;
    d) dir=$OPTARG ;;
    *)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done
shift $(( OPTIND - 1 ))

# --- Check Arguments
errors=""

#[[ -z "$dir" ]] && errors="${errors}A folder must be specified. "

if [[ ! -z "$errors" ]]
then
  trace $errors
  exit 1
fi

# =================================================
# main
# =================================================
rm ${tmpFile}* 2>/dev/null

rm bayesian*.csv
#python bayesian.py --stop 1 --ph 1
#ython bayesian.py --stop 1 --ph 0
#python bayesian.py --stop 0 --ph 1
python bayesian.py --stop 0 --ph 0
ls -la  bayesian*.csv

rm ${tmpFile}* 2>/dev/null

