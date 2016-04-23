#!/usr/bin/env python3
import json
import sys

def process_file(filename):
    document = json.load(open(filename))
    paragraphs = ['\n'.join([''.join(map(lambda x: x['raw'], sent)) 
                    for sent in par])
                    for par in document['text']]
    open(filename + '.txt', 'w').write('\n\n'.join(paragraphs))

filenames = sys.argv[1:]
for filename in filenames:
    process_file(filename)
