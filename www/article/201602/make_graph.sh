#!/bin/bash

set -ex

AGNER=~/dev/agner/agner
OUT=$(pwd)

${AGNER} -r E5-2697v3.json --png "${OUT}/haswell_{test}_{subtest}_resteers.png" --dpi 70 plot 'btb_size.*' --alt
${AGNER} -r E5-2697v3.json --png "${OUT}/haswell_{test}_{subtest}" --dpi 100 plot 'btb_size.*' --xsize 18 --ysize 10
${AGNER} -r E5-2667v2.json --png "${OUT}/ivy_{test}_{subtest}_resteers.png" --dpi 70 plot 'btb_size.*' --alt
${AGNER} -r E5-2667v2.json --png "${OUT}/ivy_{test}_{subtest}.png" --dpi 100 plot 'btb_size.*' --xsize 18 --ysize 10
mogrify -verbose -trim -resize '350x' ivy*resteers.png haswell*resteers.png
