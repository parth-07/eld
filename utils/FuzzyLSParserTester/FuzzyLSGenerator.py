#!/usr/bin/env python3

import argparse
from random import randrange

def create_parser():
  parser = argparse.ArgumentParser(prog="FuzzyLSGenerator",
                      description=("FuzzyLSGenerator takes a good linker script"
                                   "and transforms it into a fuzzed linker script."))
  parser.add_argument("input", help="Input file")
  parser.add_argument("output", help="Output file")
  parser.add_argument("--delete-count", "-d", type=int, default = 1,
          help="Number of tokens to delete in the good linker script")
  return parser

if __name__ == "__main__":
  parser = create_parser()
  args = parser.parse_args()
  input_filename = args.input
  with open(input_filename, "r") as f:
    contents = f.read()
    tokens = contents.split(' ')
    tokens_to_delete = []
    i = 0
    while i < args.delete_count:
      to_delete = randrange(len(tokens))
      print("Removed token({idx}): {tok}".format(idx=to_delete, tok=tokens[to_delete]))
      del tokens[to_delete]
      i += 1
    contents = " ".join(tokens)
  output_filename = args.output
  # print(contents)
  with open(output_filename, "w") as f:
    f.write(contents)

