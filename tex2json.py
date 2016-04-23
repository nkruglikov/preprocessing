#!/usr/bin/env python3
import sys
import re
import subprocess
import string
import nltk
import pickle
import json

def detex(string):
    buf = bytes(string, encoding='utf8')
    return subprocess.check_output(['detex', '-l'], input=buf).decode('utf8')

def normalize(string):
    return re.sub(r'(\s)+', r' ', string)

def mystem(string):
    buf = bytes(string, encoding='utf8')
    return subprocess.check_output(['./mystem', '-c', '-d', '--format=json'],
            input=buf).decode('utf8')

# Define regexps
re_title = re.compile(r'\\title.*?\{(.*?)\}', re.DOTALL|re.L|re.M)
re_author = re.compile(r'\\author.*?\{(.*?)\}', re.DOTALL|re.L|re.M)
re_text = re.compile(r'\\maketitle(.*)\\end\{document\}', re.DOTALL|re.L|re.M)

# Get document
tex_filename = sys.argv[1]
raw_tex = open(tex_filename).read()
print('Processing %s...' % tex_filename)

try:
    # Get title, author and text from document
    title = normalize(detex(re.search(re_title, raw_tex).groups()[0]))
    author = normalize(detex(re.search(re_author, raw_tex).groups()[0]))
    text = detex(re.search(re_text, raw_tex).groups()[0])

    # Get paragraphs from document
    paragraphs = text.split('\n\n')
    paragraphs = list(filter(
        lambda x: not(set(x) < set(string.whitespace)), paragraphs))

    # Split paragraphs into sentences
    russian = pickle.load(open('russian.pickle', 'rb'))
    paragraphs = list(map(
        lambda x: russian.tokenize(normalize(x)),
        paragraphs))

    # Build resulting document
    document = {'author': author, 'title': title}
    document['text'] = []
    for p in paragraphs:
        paragraph = []
        for s in p:
            analisys = json.loads(mystem(s))
            sentence = []
            for w in analisys:
                token = {'raw': w['text']}
                if 'analysis' in w and len(w['analysis']) > 0:
                    token['lex'] = w['analysis'][0]['lex']
                sentence.append(token)
            paragraph.append(sentence)
        document['text'].append(paragraph)

    open(tex_filename + '.json', 'w').write(json.dumps(document,
        ensure_ascii=False))
except Exception as err:
    print("ERROR:", err)
