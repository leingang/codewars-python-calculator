#!/usr/bin/env python


import codewars_test as Test
from calc import calc
# (random, eval) = __import__('extract.randomPassWord5752FFG2')
import random

def do():
    def testing(act,exp):
        Test.expect(abs(act-exp) < 1e-6, "{} should equal {}".format(act,exp))
    
    Test.it("Fixed tests")
    tests = [
        ["2 + 3 * 4 / 3 - 6 / 3 * 3 + 8", 8],
        ["1 + 2 * 3 * 3 - 8", 11],
        ["1 + 2 * 3 * (5 - 2) - 8", 11],
        ["1 + 2 * 3 * (5 - (3 - 1)) - 8", 11],
        ["4 + -(1)", 3],
        ["4 - -(1)", 5],
        ["4 * -(1)", -4],
        ["4 / -(1)", -4],
        ["-1", -1],
        ["-(-1)", 1],
        ["-(-(-1))", -1],
        ["-(-(-(-1)))", 1],
        ["(((((-1)))))", -1],
        ["5 - 1", 4],
        ["5- 1", 4],
        ["5 -1", 4]
    ]
    
    try:
        if calc("'x'") == "x": Test.expect(False, "Trying to use eval?")
    except: pass
    
    for test in tests:
        testing(calc(test[0]), test[1])
    
    Test.it("Random tests")
    for i in range(100):
        try:
            expression = "{}{} {} {}{} {} {}{} {} {}{} {} {}{} {} {}{} {} {}{} {} {}{}".format(random.choice(["-", ""]), random.randint(1, 100), random.choice(["+", "-", "*", "/"]), random.choice(["-", ""]), random.randint(1, 100), random.choice(["+", "-", "*", "/"]), random.choice(["-", ""]), random.randint(1, 100), random.choice(["+", "-", "*", "/"]), random.choice(["-", ""]), random.randint(1, 100), random.choice(["+", "-", "*", "/"]), random.choice(["-", ""]), random.randint(1, 100), random.choice(["+", "-", "*", "/"]), random.choice(["-", ""]), random.randint(1, 100), random.choice(["+", "-", "*", "/"]), random.choice(["-", ""]), random.randint(1, 100), random.choice(["+", "-", "*", "/"]), random.choice(["-", ""]), random.randint(1, 100))
            testing(calc(expression), eval(expression))
        except ZeroDivisionError: pass
    
    for i in range(100):
        try:
            expression = "{}({}{}) {} ({}{} {} {}{} {} {}({})) {} ({}{} {} {}((({}({}{} {} {}{})))) {} {}{})".format(random.choice(["-", ""]), random.choice(["-", ""]), random.randint(1, 100), random.choice(["+", "-", "*", "/"]), random.choice(["-", ""]), random.randint(1, 100), random.choice(["+", "-", "*", "/"]), random.choice(["-", ""]), random.randint(1, 100), random.choice(["+", "-", "*", "/"]), random.choice(["-", ""]), random.randint(1, 100), random.choice(["+", "-", "*", "/"]), random.choice(["-", ""]), random.randint(1, 100), random.choice(["+", "-", "*", "/"]), random.choice(["-", ""]), random.choice(["-", ""]), random.choice(["-", ""]), random.randint(1, 100), random.choice(["+", "-", "*", "/"]), random.choice(["-", ""]), random.randint(1, 100), random.choice(["+", "-", "*", "/"]), random.choice(["-", ""]), random.randint(1, 100))
            testing(calc(expression), eval(expression))
        except ZeroDivisionError: pass
    
    for i in range(100):
        expression = "{}{}- {}{}- {}{}- {}{}".format(random.choice(["-", ""]), random.randint(1, 100), random.choice(["-", ""]), random.randint(1, 100), random.choice(["-", ""]), random.randint(1, 100), random.choice(["-", ""]), random.randint(1, 100))
        testing(calc(expression), eval(expression))
do()