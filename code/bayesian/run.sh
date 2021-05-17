#!/bin/bash

graphics=$(cat<<EOD|grep -v '^#'|sed -e 's/  */#/g'
# Strategy      TotC   Tot every experiment      local=0/global=1
#CBasic         20     1000                       0
#CBayesian      20     1000                       0
#CHelstrom      20     1000                       0
CBayesianTheory 20     0                          0
#CBayesianTheory 20     0                          1
#CSquareRoot     20     0                          0
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
  if [[ "$class" == "CBayesianTheory" || "$class" == "CSquareRoot" ]]
  then
      echo "Theory"
      python theory.py  --class ${class} --totC ${totC} --glob ${global} --csv ${file}
  else
    echo "Experiment"
    if [ -f $file ]
    then
      echo "SKIP, file $file exist!"
    else
      echo "Generating class=${class}, totC=${totC}, tot=${tot}, global=${global} into ${file}..."
      python experiments.py  --class ${class} --totC ${totC} --tot ${tot} --glob ${global} --csv ${file}
      echo "File $file generated!"
    fi
  fi

  ls -la $file
done
