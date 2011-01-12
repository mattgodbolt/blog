#!/usr/bin/env python
import os, sys
import re


HEADER = """
application: godboltblog
version: 1
runtime: python
api_version: 1

default_expiration: "12h"

handlers:
"""

def resafe(r):
  return re.escape(r)

def main():
  out = open('newapp.yaml', 'w')
  out.write(HEADER)
  basedir = os.path.realpath('../htdocs')
  for base, dirs, files in os.walk(basedir):
    relative_base = base[len(basedir)+1:]
    for file in files:
      name, ext = os.path.splitext(file)
      out.write('- url: ' + relative_base + '/' + resafe(name) + '(' + resafe(ext) + ')?\n')
      out.write('  static_files: ../htdocs/' + relative_base + file + '\n')
      out.write('  upload:  ../htdocs/' + relative_base + file + '\n')
  out.close()


if __name__ == '__main__':
  main()

