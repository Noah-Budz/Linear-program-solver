## Author
Name: Noah Budz
Student id: V00966850


## Usage
To use this program, run the following command:
```sh
python3 lp_solver.py < [INPUT]
```
where `[INPUT]` is the given linear program in standard form in the specified format

## This solver uses the dictionary-based Simplex Method to solve linear programs given in standard form.
 The linear program is read in from standard input and converted into a dictionary. A secondary list of indexes is also created, storing the `(x,y)` coordinates of the optimization and slack variables. Then  the initial dictionary is checked 
 for infeasibility. If feasible, the program uses the Simplex Method. If infeasible, the Two-Phase-Dual-Primal Method is run. Entering and leaving variables are chosen using the Largest Increase Rule. If a degeneracy occurs, Bland's Rule is used 
 instead to prevent cycling. Then check for unboundedness, using the leaving index to ensure that there is at least one non-positive value in the column. If there is none, the leaving index will be it's original invalid value, and the program 
 will terminate. The program then performs a pivot operation, switching the entering column with the leaving row. All other relevant values in the dictionary are also updated accordingly, with epsilon comparison and float truncation to ensure that 
 floating-point errors do not hinder execution. If there are no more non-positive coefficients in the objective function, the solution is printed out. Otherwise the Solver continues to run

## Cycle Prevention
Largest Increase Rule is used to pick entering and leaving variables until a degeneracy occurs. If one is found, the program switches to using Bland's Rule to ensure that cycling does not occur.

## Extra Features
The following feature from the Specification PDF have been implemented in this program:
 Primal-Dual Methods: The Two-Phase-Dual-Primal Method is used to find an initially feasible dictionary if it exists.

 	If a dictionary is found to be initially infeasible, the dual of the given dictionary is computed by taking the negative transpose. The objective function is then zero-ed out in  the dual, with the original objective function. The `solve` 
method is then used on the dual linear program with an objective function of c = 0 to find the optimal dual. If no leaving variable can be found, this indicates that the dual is unbounded, meaning the primal is infeasible, and so the program 
outputs `infeasible`. If an optimal dual is found, the new feasible primal dictionary is retrieved. Finally, the program runs simplex on the primal dictionary and solves it.