#!/usr/bin/env python3

import argparse
from random import randrange
import sys
import re


def create_parser():
    parser = argparse.ArgumentParser(
        prog="CompareLinkerScripts",
        description=(
            "CompareLinkerScripts takes two linker scripts. "
            "It returns true if the two scripts are equivalent; "
            "Otherwise returns false."
        ),
    )
    parser.add_argument("script1", help="script1")
    parser.add_argument("script2", help="script2")
    return parser


def comment_remover(text):
    def replacer(match):
        s = match.group(0)
        if s:
            return " "
        else:
            return s

    pattern = re.compile(
        r"//.*?$|/\*.*?\*/",
        re.DOTALL | re.MULTILINE,
    )
    return re.sub(pattern, replacer, text)


def tokenize(text):
    pos = 0
    tokens = []
    # print(text)
    for i in range(len(text)):
        if not (text[i].isalnum() or text[i] in ['/', '.']):
            if pos < i:
                tokens.append(text[pos:i])
            if text[i].isspace():
                pos = i + 1
            else:
                pos = i
    if pos <= len(text) - 1:
        tokens.append(text[pos:])
    return tokens

def compare_scripts(script1, script2):
    with open(script1, "r") as f:
        contents1 = f.read()
        comment_remover(contents1)
        tokens1 = tokenize(contents1)
    with open(script2, "r") as f:
        contents2 = f.read()
        comment_remover(contents2)
        tokens2 = tokenize(contents2)
    # print(tokens1)
    # print(tokens2)
    if len(tokens1) != len(tokens2):
        return False
    for i in range(len(tokens1)):
        try:
            v1 = int(tokens1[i], 0)
            v2 = int(tokens2[i], 0)
            if v1 != v2:
                return False
        except ValueError:
            if tokens1[i] != tokens2[i]:
                return False
    return True

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    script1 = args.script1
    script2 = args.script2
    if compare_scripts(script1, script2):
        sys.exit(0)
    sys.exit(1)
