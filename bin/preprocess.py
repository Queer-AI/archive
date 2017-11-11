#!/usr/bin/env python

import os
import csv
import re
import urllib

INPUT_URL = "https://s3-us-west-1.amazonaws.com/queer-ai/corpus/literotica.csv"
INPUT_FILE = "train/literotica.csv"
DATA_DIR = "train/"

VALID_FRAC = .01
TEST_FRAC = .01
VOCAB_SIZE = 40000
RE_CHUNK_SIZE = 100000

chars = ""

if not os.path.isfile(INPUT_FILE):
    urllib.urlretrieve(INPUT_URL, INPUT_FILE)

with open(INPUT_FILE, 'r+') as data_file:
    for line in csv.DictReader(data_file):
        chars += line['story']

def sub_chunked(regex, sub, text):
    """Certain regexes, esp lookahead, use dramatically more memory to parse than
    the actual string takes up. So we split into chunks, run the substitutions, then
    reassenble the string """
    cur = 0
    ret = ""
    chunk = ""
    while cur < len(text):
        start = cur
        cur += RE_CHUNK_SIZE
        cur = min(cur, len(text))
        while cur < (len(text) - 1) and text[cur] != " ":
            cur += 1
        chunk = text[start:cur]
        ret += re.sub(regex, sub, chunk)
    return ret


def cleanup(chars):
    output = chars.lower()
    output = sub_chunked("([^.!a-z0-9' ])", "", output)
    output = sub_chunked("([\.|!]) ?", "\n", output)
    output = sub_chunked("\n+", " \n", output)
    output = sub_chunked(" +", " ", output)
    return output


def limit_vocab(chars, vocab):
    def limit_word(word):
        if word in vocab:
            return word
        else:
            return "<unk>"
    ret = ""
    cur = 0
    prev = 0
    while(cur < len(chars)):
        if chars[cur] == " ":
            ret += limit_word(chars[prev:cur])
            ret += " "
            prev = cur + 1
        cur += 1

    return ret

def save_data(chars, name):
    _from = ""
    _to = ""
    i = 0
    for line in chars.split("\n"):
        i += 1
        if i % 2 == 0:
            _from += line + "\n"
        else:
            _to += line + "\n"
    with open(DATA_DIR + name + "_from.txt", "w") as data:
        data.write(_from)
    with open(DATA_DIR + name + "_to.txt", "w") as data:
        data.write(_to)
    print("wrote %s" % name)


# remove rare words
word_count = {}
def count_word(word):
    if word in word_count:
        word_count[word] += 1
    else:
        word_count[word] = 1

chars = cleanup(chars)
print('cleaned up')
cur = 0
prev = 0
while(cur < len(chars)):
    if chars[cur] == " ":
        count_word(chars[prev:cur])
        prev = cur + 1
    cur += 1
print("loaded words")
vocab = sorted(word_count.iteritems(), key=lambda (k,v): (v,k))
print("sorted words")
vocab.reverse()
vocab = map(lambda (i): i[0], vocab[:VOCAB_SIZE])
print("limited vocabulary")


valid_end = int(len(chars) * VALID_FRAC)
test_end = valid_end + int(len(chars) * TEST_FRAC)

save_data(limit_vocab(chars[:valid_end], vocab), "valid")
save_data(limit_vocab(chars[valid_end:test_end], vocab), "test")
save_data(limit_vocab(chars[test_end:], vocab), "train")
