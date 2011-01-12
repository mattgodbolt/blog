#!/bin/bash
# Create distribution tarball

if [ ! -f ./dist.sh ]; then
  echo dist.sh must be run from the directory it is contained in.
  exit 1
fi

DESTDIR=/tmp
DEST=$DESTDIR/mbs

VERSION=`svnversion -n .`
echo Making tarball for MBS r$VERSION

rm -rf $DEST
svn export -q . $DEST
svn export -q generator/src/etl $DEST/generator/src/etl
echo "dev (r$VERSION)" > $DEST/doc/VERSION

# Remove the following files from the tarball.
rm $DEST/dist.sh $DEST/scripts/validate-feed
mv $DEST/www/article/notes/article-format.txt $DEST/doc/article-format
rm -rf $DEST/www/
mkdir -p $DEST/www/{article,archive,feed}

cat > $DEST/www/article/sample.text << EOF
My first post
Date: 2007-05-24 11:20:01
Summary: It's not a bad start, is it?
Label: meta

This is my _very first_ blog post.  Isn't it great?
EOF

# Make a tarball.
cd $DESTDIR
tar jcf mbs-r$VERSION.tar.bz2 mbs/
rm -rf mbs

echo Created $DESTDIR/mbs-r$VERSION.tar.bz2
