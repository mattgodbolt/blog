#!/bin/bash

set -euo pipefail

rm -rf out
mkdir out out/htdocs out/htdocs_fixup

rsync -rlp --exclude=/article www/ out/htdocs
rsync -rlp --include='*.html' --include='*.png' --include='*.jpeg' --include='*.py' --include='*.zip' --include='*.cpp' --include='*/' --include='**/media/***' --exclude='*' www/article/ out/htdocs

aws s3 sync out/htdocs/ s3://web.xania.org/

fixup() {
    EXT=$1
    CT=$2
    DIR=$3
    for file in $(cd out/htdocs && find ${DIR} -name "*.${EXT}"); do
        mkdir -p out/htdocs_fixup/$(dirname ${file})
        cp -a out/htdocs/${file} out/htdocs_fixup/${file%.${EXT}}
    done
    aws s3 sync out/htdocs_fixup/ s3://web.xania.org/ --content-type ${CT} --cache-control max-age=30 --metadata-directive REPLACE
}

fixup html text/html .
fixup atom application/rss+xml feed
aws s3 cp out/htdocs/feed.atom s3://web.xania.org/feed --content-type application/rss+xml --cache-control max-age=30 --metadata-directive REPLACE
aws cloudfront create-invalidation --distribution-id E2QLYX3P4WX0GV --paths '/*'
