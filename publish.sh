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
