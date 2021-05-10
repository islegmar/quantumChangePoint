#!/bin/bash

graphics=$(cat<<EOD|grep -v '^#'|sed -e 's/  */#/g'
# Strategy      TotC   Tot every experiment      local=0/global=1
#CBasic         20     1000                       0
#CBayesian      20     1000                       0
#CHelstrom      20     1000                       0
CBayesianTheory 20     0                          1
CSquareRoot     20     0                          0
# --------- Local vs Global
#CBayesian     20     1000                       0
#CBayesian     20     1000                       1
#CBasic        10     500                        0
#CBasic        10     500                        1
EOD)

for line in $graphics
do
  class=$(echo $line|cut -d '#' -f 1,1)
  totC=$(echo $line|cut -d '#' -f 2,2)
  tot=$(echo $line|cut -d '#' -f 3,3)
  global=$(echo $line|cut -d '#' -f 4,4)

  file="data/${class}-${totC}-${tot}-global${global}.csv"
  if [[ "$class" -eq "CBayesianTheory" || "$class" -eq "CSquareRoot" ]]
  then
      echo "Theory"
      python theory.py  --class ${class} --totC ${totC} --glob ${global} --csv ${file}
  else
    if [ -f $file ]
    then
      echo "SKIP, file $file exist!"
    else
      echo "Generating class=${class}, totC=${totC}, tot=${tot}, global=${global} into ${file}..."
      # python experiments.py  --class ${class} --totC ${totC} --tot ${tot} --glob ${global} --csv ${file}
      echo "File $file generated!"
    fi
  fi

  ls -la $file
done

# ================ OLD STUFF
exit 0

totC=20
tot=1000

# opts=""
# if [ $isGlobal -eq 1 ]
# then
#   opts="$opts --glob"
# fi


cat<<EOD
===============================================
Getting numerical data for:
- # of 'c' values checked : ${totC}
- # of times every experiment is executed : ${tot}

Press any key to continue
===============================================

EOD
read

touch /tmp/$(basename $0)

echo ">>>> Running Local (local) ...."
python experiments.py        --class CBasic  --totC ${totC} --tot ${tot} --csv data/basic-${totC}-${tot}-global0.csv
#echo ">>>> Running Local (global) ...."
#python experiments.py --glob --class CBasic  --totC ${totC} --tot ${tot} --csv data/basic-${totC}-${tot}-global1.csv

echo ">>>> Running Bayesian (local) ...."
python experiments.py        --class CBayesian --totC ${totC} --tot ${tot} --csv data/bayesian-${totC}-${tot}-global0.csv
# echo ">>>> Running Bayesian (global) ...."
# python experiments.py --glob --class CBayesian --totC ${totC} --tot ${tot} --csv data/bayesian-${totC}-${tot}-global1.csv

echo "Files generated:"
find data -type f -name '*.csv' -mindepth 1 -maxdepth 1 -newer /tmp/$(basename $0)
