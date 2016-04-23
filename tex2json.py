#!/usr/bin/env python3
import sys
import re
import subprocess
import string
import nltk
import pickle
import json

# Define regexps
re_title = re.compile(r'\\title.*?\{(.*?)\}', re.DOTALL|re.L|re.M)
re_author = re.compile(r'\\author.*?\{(.*?)\}', re.DOTALL|re.L|re.M)
re_text = re.compile(r'\\maketitle(.*)\\end\{document\}', re.DOTALL|re.L|re.M)
#re_norm_spaces = re.compile(r'(\s)+', re.DOTALL|re.L|re.M)
#re_norm_mystem = re.compile(r'\?+\}', re.DOTALL|re.L|re.M)
#re_jsonize = re.compile(r'(\w*)\{(.*?)\}', re.DOTALL|re.L|re.M)
#re_split_mystem = re.compile(r'(\w*\{.*?\})', re.DOTALL|re.L|re.M)

def detex(string):
    buf = bytes(string, encoding='utf8')
    return subprocess.check_output(['detex', '-l'], input=buf).decode('utf8')

def normalize(string):
    return re.sub(r'(\s)+', r' ', string, re.M|re.L|re.DOTALL)

def mystem(string):
    buf = bytes(string, encoding='utf8')
    analysis = subprocess.check_output(['./mystem', '-c', '-d'],
            input=buf).decode('utf8')
    return re.sub(r'\?+\}', r'}', analysis, re.M|re.L|re.DOTALL)

def jsonize(word):
    result = {}
    search = re.search(r'(\w*)\{(.*?)\}', word)
    if search is not None:
        raw, lex = search.groups()
        result['raw'] = raw
        result['lex'] = lex
    else:
        result['raw'] = word
    return result

def process_tex(tex_filename):
    raw_tex = open(tex_filename).read()
    print('Processing %s...' % tex_filename)

    # Get title, author and text from document; apply mystem
    title = normalize(detex(re.search(re_title, raw_tex).groups()[0]))
    author = normalize(detex(re.search(re_author, raw_tex).groups()[0]))
    text = mystem(detex(re.search(re_text, raw_tex).groups()[0]))

    # Get paragraphs from document
    paragraphs = text.split('\n\n')
    paragraphs = filter(
        lambda x: not(set(x) < set(string.whitespace)), paragraphs)

    # Split paragraphs into sentences
    russian = pickle.load(open('russian.pickle', 'rb'))
    paragraphs = map(
        lambda x: russian.tokenize(normalize(x)),
        paragraphs)

    # Build resulting document
    document = {'author': author, 'title': title}
    document['text'] = []
    for p in paragraphs:
        paragraph = []
        for s in p:
            sentence = [jsonize(w) for w in
                    re.split(r'(\w*\{.*?\})', s, re.L|re.M|re.DOTALL)]
            paragraph.append(sentence)
        document['text'].append(paragraph)

    open(tex_filename + '.json', 'w').write(json.dumps(document,
        ensure_ascii=False))

for filename in sys.argv[1:]:
    try:
        process_tex(filename)
    except Exception as err:
        print("ERROR:", err)
