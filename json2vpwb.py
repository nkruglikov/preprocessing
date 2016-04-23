import json
import sys
from collections import defaultdict
from string import whitespace

def get_words(document):
    words = defaultdict(int)
    for par in document['text']:
        for sent in par:
            for word in sent:
                if 'lex' in word and not(set(word['lex']) < set(whitespace)):
                    words[word['lex']] += 1
    return words

def get_words_number(words):
    return ' '.join(
            map(lambda x: "%s:%d"%(x[0], x[1]), 
                sorted(
                    words.items(),
                    key=lambda x: x[1])
            ))

def process_file(filename):
    document = json.load(open(filename))
    return filename[:-9] + ' ' + get_words_number(get_words(document))

def process_collection(filenames):
    return '\n'.join(process_file(filename) for filename in filenames)


filenames = sys.argv[1:]
open('collection.vpwb', 'w', encoding='utf8').write(
        process_collection(filenames))
