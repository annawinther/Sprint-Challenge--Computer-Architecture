#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

# program = [
#         # From print8.ls8
#         0b10000010, # LDI R0,8
#         0b00000000,
#         0b00001000,
#         0b01000111, # PRN R0
#         0b00000000,
#         0b00000001, # HLT
#     ]
program = []
filename = sys.argv[1]
with open(filename) as f:
        for line in f:
            # print(line)
            # split line before and after comment symbol
            comment_split = line.split("#")

            # # extract our number
            num = comment_split[0].strip() # trim whitespace

            if num == '':
                continue # ignore blank lines

            # convert our binary string to a number
            val = int(num, 2)

            # store val at address in memory
            program.append(val)

cpu = CPU()

cpu.load(program)
cpu.run()
