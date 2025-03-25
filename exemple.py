from mip import Model, xsum, minimize, maximize, BINARY, OptimizationStatus

def KP ():
    # Read data from text file
    n=4
    items =['A', 'B', 'C', 'D']
    weights = [5,7,4,6]
    values = [10,13,8,11]
    capacity = 15

    # Create the model
    model = Model("Knapsack")

    # Decision variables
    take = [model.add_var(var_type=BINARY) for i in range(n)]

    # Objective function
    model.objective = maximize(xsum(values[i] * take[i] for i in range(n)))

    # Constraint
    model += xsum(weights[i] * take[i] for i in range(n)) <= capacity


    # Create the model
    # Solve the problem
    status = model.optimize(max_seconds=2)

    # Output
    print("Status:", OptimizationStatus(status))
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        print("Total Value =", model.objective_value)
        for i in range(len(items)):
            if take[i].x == 1:
                print(items[i], ": Taken")

KP()


def solve_assignment_problem(cost_matrix):
    """Solves the assignment problem using mip."""

    num_workers = len(cost_matrix)
    num_tasks = len(cost_matrix[0])

    if num_workers != num_tasks:
        raise ValueError("Cost matrix must be square (equal number of workers and tasks).")

    model = Model("Assignment")

    # Decision variables: x[i][j] = 1 if worker i is assigned to task j, 0 otherwise
    x = [[model.add_var(var_type=BINARY) for j in range(num_tasks)] for i in range(num_workers)]

    # Objective function: Minimize the total cost
    model.objective = minimize(xsum(cost_matrix[i][j] * x[i][j] for i in range(num_workers) for j in range(num_tasks)))

    # Constraints:
    # 1. Each worker is assigned to exactly one task
    for i in range(num_workers):
        model += xsum(x[i][j] for j in range(num_tasks)) == 1

    # 2. Each task is assigned to exactly one worker
    for j in range(num_tasks):
        model += xsum(x[i][j] for i in range(num_workers)) == 1

    # Solve the problem
    status = model.optimize()

    # Output
    if status == OptimizationStatus.OPTIMAL:
        print("Optimal solution found!")
        print("Total cost:", model.objective_value)
        for i in range(num_workers):
            for j in range(num_tasks):
                if x[i][j].x == 1:
                    print(f"Worker {i+1} assigned to Task {j+1}")
    else:
        print("No optimal solution found.")

# Example usage
cost_matrix = [
    [8, 5, 6, 7],
    [7, 6, 4, 9],
    [9, 8, 7, 5],
    [6, 9, 5, 8]
]

solve_assignment_problem(cost_matrix)

def solve_bin_packing(item_sizes, bin_capacity):
    """Solves the bin packing problem using lists of lists."""

    num_items = len(item_sizes)
    num_bins = num_items

    model = Model("BinPackingList")

    # Decision variables: x[i][j]
    x = [[model.add_var(var_type=BINARY) for j in range(num_bins)] for i in range(num_items)]

    # y[j] = 1 if bin j is used, 0 otherwise
    y = [model.add_var(var_type=BINARY) for j in range(num_bins)]

    # Objective function: Minimize the number of bins used
    model.objective = minimize(xsum(y[j] for j in range(num_bins)))

    # Constraints:
    # 1. Each item is placed in exactly one bin
    for i in range(num_items):
        model += xsum(x[i][j] for j in range(num_bins)) == 1

    # 2. The total size of items in a bin does not exceed its capacity
    for j in range(num_bins):
        model += xsum(item_sizes[i] * x[i][j] for i in range(num_items)) <= bin_capacity * y[j]

    for j in range(num_bins-1):
        model+=y[j+1]<=y[j]
    # Solve the problem
    status = model.optimize()

    # Output
    if status == OptimizationStatus.OPTIMAL:
        print("Optimal solution found!")
        print("Number of bins used:", model.objective_value)
        for j in range(num_bins):
            if y[j].x == 1:
                print(f"Bin {j+1}:")
                for i in range(num_items):
                    if x[i][j].x == 1:
                        print(f"  Item {i+1} (size {item_sizes[i]})")
    else:
        print("No optimal solution found.")

# Example usage
item_sizes = [3, 5, 2, 7, 4, 6, 1, 8]
bin_capacity = 10
solve_bin_packing(item_sizes, bin_capacity)