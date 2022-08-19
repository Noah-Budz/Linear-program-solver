from sys import float_info, stdin
from re import split
from math import isclose, trunc


def negate(num):
    """
    negates the given number
    """
    return num * -1


def is_close(a, b):
    """
    checks if two numbers are within a small enough tolerance to be equal to eachother
    """
    return isclose(a, b, abs_tol=0.0000001)


def truncate(num):
    """
    truncates float to 10 decimals 
    """
    step = 10.0 ** 10
    return trunc(step * num) / step


def normalize(num):
    """
    truncates number or if its close enough to 0 returns 0
    """
    if abs(num) > 0.0000001:
        return truncate(num) 
    else:
        return 0


def natural_sort(array):
    """
    sorts array so x1 comes before x2 before x3, etc
    """
    convert = lambda l: int(l) if l.isdigit() else l
    natural_key = lambda d: [convert(val) for val in split('([0-9]+)', d["label"])]

    return sorted(array, key=natural_key)


def get_dual(dictionary):
    """
    gets the dual by negative transpose
    """
    transposed = list(map(list, zip(*dictionary)))
    
    return [[negate(coeff) if not is_close(coeff, 0) else 0 for coeff in row] for row in transposed]


def get_objective_value(dictionary):
    """
    returns objective value of input dictionary
    """
    return dictionary[0][0]


def get_solution_vector(indexes, dictionary):
    """
    returns solution x for x in {x1,x2,x3...}
    """
    nonbasic_vars = list(filter(lambda d: 'x' in d["label"], indexes))
    solution_vector = [dictionary[d["y"]][d["x"]] if d["y"] != 0 else 0 for d in nonbasic_vars]

    return solution_vector


def print_float(num, no_new_line=False):
    """
    prints number to 7 decimal places for output
    """
    print(str(float('%.7g' % num)).rstrip('0').rstrip('.'), end=' ' if no_new_line else '\n')


def print_optimal(objective_value, location):
    """
    if optimal solution is found prints out solution info
    """
    print("optimal")
    print_float(objective_value)
    [print_float(coor, True) for coor in location]
    print()


def convert_constraints(constraint):
    """
    converts constraint from an LP into dictionary form
    """
    new_constraint = [constraint[-1]]
    constraint = list(map(
        lambda x: negate(x) if x != 0 else x,
        constraint[:-1]
    ))
    new_constraint.extend(constraint)

    return new_constraint


def readinput():
    """
    reads standard input file and creates a dictionary
    """

    objective_function = [0]
    objective_function.extend([float(coeff) for coeff in stdin.readline().strip().split()])

    constraints = []
    for line in stdin.readlines():
        constraints.append([float(coeff) for coeff in line.strip().split()])

    constraints = list(map(convert_constraints, constraints))

    dictionary = [objective_function] + constraints

    return dictionary


def get_entering(dictionary, indexes, is_degenerate, is_primal):
    """
    gets the entering variable for dictionary with largest increase or blands if degenerate
    """
    zero_index = 'y' if is_primal else 'x'
    comp_index = 'x' if is_primal else 'y'

    # Pick entering using Largest Increase Rule
    if not is_degenerate:
        entering_val = max(dictionary[0][1:])
        entering_index = dictionary[0][1:].index(entering_val) + 1
        return entering_index

    # Pick entering using Bland's Rule
    bland_indexes = natural_sort([dict for dict in indexes if dict[zero_index] == 0])
    for dict in bland_indexes:
        if dictionary[0][dict[comp_index]] > 0:
            entering_index = dict[comp_index]
            break

    return entering_index


def get_leaving(dictionary, indexes, entering_index, is_degenerate, is_primal):
    """
    gets leaving variable for dictionary using largest increase or blands if degenerate
    """
    zero_index = 'x' if is_primal else 'y'
    leaving_val = float_info.max
    leaving_index = 'Invalid'

    # Pick leaving using smallest bound on entering variable
    if not is_degenerate:
        for i, row in enumerate(dictionary[1:], start=1):
            if ((row[entering_index] < 0) and (negate(row[0] / row[entering_index])) < leaving_val):
                leaving_index = i
                leaving_val = normalize(negate(row[0] / row[entering_index]))

        return leaving_index

    # Pick leaving using Bland's Rule
    leaving_indexes = [dict for dict in indexes if dict[zero_index] == 0]
    possible_pivots = []

    for i, row in enumerate(dictionary[1:], start=1):
        if row[entering_index] < 0:
            possible_pivots.append({
                "index": i,
                "label_prefix": leaving_indexes[i - 1]["label"][:1],
                "label_index": int(leaving_indexes[i - 1]["label"][2:]),
                "val": normalize(negate(row[0] / row[entering_index]))})

    possible_pivot_x = min(
        sorted([dict for dict in possible_pivots if dict["label_prefix"] == 'x'], key=lambda k: k['label_index']),
        key=lambda k: k["val"], default={"index": 'Invalid', "val": float_info.max})
    
    possible_pivot_z = min(
        sorted([dict for dict in possible_pivots if dict["label_prefix"] == 'z'], key=lambda k: k['label_index']),
        key=lambda k: k["val"], default={"index": 'Invalid', "val": float_info.max})


    leaving_dict = (
        possible_pivot_x
        if bool(possible_pivot_x) and possible_pivot_x['val'] < possible_pivot_z['val']
        else possible_pivot_z
    )
        
    leaving_index = leaving_dict["index"]

    return leaving_index


def create_indexes(dictionary):
    """
    creates list of indices of locations of x and slack z variables
    """
    var_indexes = [({ "label": f'x {i}', "x": i, "y": 0 }) for i in range(1, len(dictionary[0]))]
    var_indexes.extend([({ "label": f'z {i}', "x": 0, "y": i }) for i in range(1, len(dictionary))])

    return var_indexes


def create_dual_indexes(dictionary):
    """
    creates list of indices of locations of x and slack z variables for dual
    """
    var_indexes = [({ "label": f'z {i}', "x": 0, "y": i }) for i in range(1, len(dictionary[0]))]
    var_indexes.extend([({ "label": f'x {i}', "x": i, "y": 0 }) for i in range(1, len(dictionary))])

    return var_indexes


def swap_indexes(entering, leaving, indexes):
    """
    swaps two indices for pivot operation
    """
    entering_index = next((i for (i, dict) in enumerate(indexes) if dict["x"] == entering))
    leaving_index = next((i for (i, dict) in enumerate(indexes) if dict["y"] == leaving))

    indexes[entering_index].update({ "x": 0, "y": leaving })
    indexes[leaving_index].update({ "x": entering, "y": 0 })

    return indexes


def swap_dual_indexes(entering, leaving, indexes):
    """
    swaps two indices for pivot operation in the dual
    """
    entering_index = next((i for (i, dict) in enumerate(indexes) if dict["y"] == entering))
    leaving_index = next((i for (i, dict) in enumerate(indexes) if dict["x"] == leaving))

    indexes[entering_index].update({ "x": leaving, "y": 0 })
    indexes[leaving_index].update({ "x": 0, "y": entering })

    return indexes


def inject_objective(dictionary, objective):
    """
    replaces first row of dictionary with objective function
    """
    for i in range(len(dictionary)):
        dictionary[i][0] = objective[i]

    return dictionary


def get_objective(dictionary):
    """
    get the objective row from dictionary
    """
    objective = []

    for i in range(len(dictionary)):
        objective.append(dictionary[i][0])
        dictionary[i][0] = 0

    return [dictionary, objective]


def handle_initially_infeasible(dictionary, indexes):
    """
    use two phase primal dual method to find feasible primal dictionary using
    dual if primal intially infeasible
    """
    if any([row[0] < 0 for row in dictionary[1:]]):
        objective_func = dictionary[0]

        dictionary[0] = [0 for i in range(len(dictionary[0]))]
        dictionary = get_dual(dictionary)
        
        [optimal_dual, var_indexes, feasible_objective_func] = solve(dictionary, objective_func)
        
        feasible_primal = get_dual(optimal_dual)
        feasible_primal[0] = feasible_objective_func
        
        return [feasible_primal, var_indexes]

    return [dictionary, indexes]


def pivot(dictionary, entering_index, leaving_index):
    """
    performs pivot operation on dictionary
    """
    pivot_point = dictionary[leaving_index][entering_index]

    dictionary[leaving_index] = [coeff / pivot_point for coeff in dictionary[leaving_index]]

    for i in range(len(dictionary)):
        if i != leaving_index:
            pivot_row = []
            dic_row = []

            for coeff in dictionary[leaving_index]:
                pivot_row.append(normalize(coeff * dictionary[i][entering_index]))

            for index, (x, y) in enumerate(zip(dictionary[i], pivot_row)):
                dic_row.append(
                    normalize(x - y)
                    if index != entering_index
                    else normalize(x / pivot_point)
                )

            dictionary[i] = dic_row

    dictionary[leaving_index] = [negate(coeff) for coeff in dictionary[leaving_index]]
    dictionary[leaving_index][entering_index] = normalize(dictionary[leaving_index][entering_index] / negate(pivot_point))

    return dictionary


def solve(dictionary, dual_objective=None):
    """
    solves LP given its dictionary form
    """
    is_primal = dual_objective == None
    is_degenerate = False
    last_objective_value = 0
    
    var_indexes = (
        create_indexes(dictionary)
        if is_primal
        else create_dual_indexes(dictionary)
    )

    if is_primal:
        [dictionary, var_indexes] = handle_initially_infeasible(dictionary, var_indexes)

    while any(coeff > 0 for coeff in dictionary[0][1:]):
        entering_index = get_entering(dictionary, var_indexes, is_degenerate, is_primal)
        leaving_index = get_leaving(dictionary, var_indexes, entering_index, is_degenerate, is_primal)

        if is_primal:
            if leaving_index == 'Invalid':
                print("unbounded")
                exit()
        else:
            if leaving_index == 'Invalid':
                print("infeasible")
                exit()

        if not is_primal:
            dictionary = inject_objective(dictionary, dual_objective)

        dictionary = pivot(dictionary, entering_index, leaving_index)

        if not is_primal:
            [dictionary, dual_objective] = get_objective(dictionary)

        var_indexes = (
            swap_indexes(entering_index, leaving_index, var_indexes)
            if is_primal
            else swap_dual_indexes(entering_index, leaving_index, var_indexes)
        )

        # Switch to Bland's Rule if degeneracy is found, to prevent cycling
        is_degenerate = is_degenerate or (isclose(last_objective_value, dictionary[0][0], abs_tol=0.0000001))
        last_objective_value = dictionary[0][0]
        
    return (
        [get_objective_value(dictionary), get_solution_vector(var_indexes, dictionary)]
        if is_primal
        else [dictionary, var_indexes, dual_objective]
    )
    

# Solve the given Linear Program
def main():
    """
    main function solves and outputs solution to LP
    """
    dictionary = readinput()

    [optimal_value, solution_vector] = solve(dictionary)
    print_optimal(optimal_value, solution_vector)



main()