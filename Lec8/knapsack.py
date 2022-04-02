#!/usr/bin/env python
import sys


def calc_estimate(problem, item_list, max_size):
    """ Calculate the value and size of the problem (overestimating the value if
        the problem contains unknowns)

        Output:
        estimate:       Estimated or true value of the problem
        size:           Estimated or true size of the problem
    """
    estimate = 0
    tot_size = 0
    # go through 'problem' where each position is matched with the sorted item_list
    for index, [item, item_size, item_value] in zip(problem, item_list):
        # add true values to estimate and tot_size
        if index == "1":
            estimate += item_value
            tot_size += item_size
        # if unknown is reached use heuristic to estimate best value
        elif index == "x":
            # don't continue if max_size is exceeded
            if tot_size >= max_size:
                break
            # if the next item is too big add a proportion of it, overestimating the value
            elif (tot_size + item_size) > max_size:
                estimate += item_value*((max_size-tot_size)/item_size)  # add proportion of item_value
                tot_size += max_size-tot_size
                break
            # add unknown item to estimate if there's room
            else:
                estimate += item_value
                tot_size += item_size

    return estimate, tot_size

# check that arguments are correct
if len(sys.argv) != 2:
    sys.exit("Usage: knapsack.py <input file>")

# open file with items
try:
    infile = open(sys.argv[1], "r")
except IOError as err:
    sys.exit("Cant open file:" + str(err))

# load in the items as a list converting numbers to floats
item_list = []
for line in infile:
    if line.startswith("#"):
        continue

    line = line.split()

    item = line[0]
    size = float(line[1])
    value = float(line[2])

    item_list.append([item, size, value])
infile.close()

# sort by value/size ratio
item_list = sorted(item_list, key=lambda x:(x[2]/x[1]), reverse = True)

# initiate parameters for branch and bound
max_size = 342
best_value = 0
stack = ["x"*len(item_list)]    # stack of a problem that only has unknowns

# branch and bound through the possible outcomes
while len(stack) > 0:
    problem = stack.pop()   # get problem from the stack

    # calculate estimated value and size of the current problem
    estimate, size = calc_estimate(problem, item_list, max_size)
    # skip problem if it is not better than previous solutions
    if estimate < best_value:
        continue
    #  or breaks size contraint
    if size > max_size:
        continue

    # if there are still unknowns in the problem then add branches to stack
    if "x" in problem:
        nextx = problem.find("x")
        stack.append(problem[:nextx] + "0" + problem[nextx+1:])
        stack.append(problem[:nextx] + "1" + problem[nextx+1:])
    # if no unknowns are left then compare with the best value
    elif estimate > best_value:
        best_value = estimate
        best_problem = problem
        best_problem_size = size


# print summary
print("Items:", sum([int(x) for x in best_problem]))
print("Combined size:", best_problem_size)
print("Combined value:", best_value)
print("Best items:", ", ".join([item for index, [item, _, _] in zip(best_problem, item_list) if index == "1"]))
