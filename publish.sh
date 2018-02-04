#!/bin/bash

set -e

mkdir -p www/feed
(cd pygen && ./main.py)

# Publish the generated and static content from www/ into htdocs/.
#
# Note that we merge the HTML contents below 'article' straight into the
# htdocs directory.  We therefore can't delete anything automatically.
#
# Note also that we use checksums (-c) rather than time to determine when
# a file has changed, because we don't update the time of the file in htdocs/
# to match the file in www/.  The reason we don't do that is because we want
# the file time updated when the contents change (so that Last-Modified is
# correct).  Using the Subversion 'use-commit-times' option might also be
# an option, but this is easier.
rsync -vc -rlp --exclude=.svn/ --exclude=/article www/ htdocs
rsync -vc -rlp --exclude=.svn/ --include='*.html' --include='*.png' --include='*.jpeg' --include='*.py' --include='*.zip' --include='*.cpp' --include='*/' --include='**/media/***' --exclude='*' www/article/ htdocs

aws s3 sync htdocs/ s3://www.xania.org/

fixup() {
    EXT=$1
    CT=$2
    rm -rf htdocs2
    mkdir -p htdocs2
    for file in $(cd htdocs && find . -name "*.${EXT}"); do
        mkdir -p htdocs2/$(dirname ${file})
        cp -a htdocs/${file} htdocs2/${file%.${EXT}}
    done
    aws s3 sync htdocs2/ s3://www.xania.org/ --content-type ${CT} --cache-control max-age=30 --metadata-directive REPLACE
    rm -rf htdocs2
}

fixup html text/html
fixup atom application/rss+xml

if [ ! -d miracle ]; then
    git clone git@github.com:mattgodbolt/miracle.git
fi
if [ ! -d miracle/roms ]; then
    aws s3 cp s3://xania.org/miracle-roms.tar.gz /tmp/
    pushd miracle
    tar zxf /tmp/miracle-roms.tar.gz
    popd
fi

(cd miracle && git pull && make dist)
aws s3 sync miracle/ s3://www.xania.org/miracle/ --exclude=".git/*" --cache-control max-age=30 --metadata-directive REPLACE
