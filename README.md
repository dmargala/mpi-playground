# mpi-playground

Examples of using mpi4py with exception handling and parallel io patterns.

## 0. MPI Optional

The zeroth set of examples demonstrate a typical mpi-optional pattern for processing data as a set of independent tasks.

### Part a

Here is the example program from [ex0-a-nompi.py](0-mpi-optional/ex0-a-nompi.py):

```python
def main():
    # say hello
    print(f"Hello!")
    # iterate over tasks
    for i in range(3):
        # read: generate data
        numbers = list(range(i * 10, (i + 1) * 10))
        print(f"({i}) numbers = {numbers}")
        # process: compute total
        total = 0
        for value in numbers:
            total += value
        # write: print result
        print(f"({i}) total = {total}")
```

The example program processes three independent tasks. 
Each task can be logically separated into the following essential steps: 

 1. **Read** (or load, generate, initialize, etc.): In this case, we are generating data on the fly but typically this would involve reading some data from disk.
 1. **Process** (or compute, analyze, etc.): This is usually the main focus of an application. Here we are summing a list of numbers.
 1. **Write** (or print, summarize, finalize, etc): Finally, the end result of the program is written to disk or a summary is printed to stdout which is what we do in this example.

Here is the result of running our first example:

```
> python ex0-a-nompi.py
Hello!
(0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
(0) total = 45
(1) numbers = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
(1) total = 145
(2) numbers = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
(2) total = 245
```

At the beginning of the program, the process says "Hello!" and proceeds to the set of tasks to process. 
The messages printed to stdout for each task are prepended with the task index in parentheses. 
For each task, we can see the numbers generated and the resulting total.

### Part b

An MPI version of the example program is implemented in [ex0-b-mpi.py](0-mpi-optional/ex0-b-mpi.py). 
The numberes for each task are generated on the root rank. 
The numbers are then broadcast to other ranks which then compute subtotals. 
The subtotals are then gathered on the root rank where the final total is computed. 
The following output shows the output running with two MPI ranks:

```
> mpiexec -n 2 python ex0-b-mpi.py
0: Hello!
1: Hello!
0: (0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
1: (0) subtotal = 25
0: (0) subtotal = 20
0: (0) total = 45
0: (1) numbers = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
0: (1) subtotal = 70
1: (1) subtotal = 75
0: (1) total = 145
0: (2) numbers = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
0: (2) subtotal = 120
0: (2) total = 245
1: (2) subtotal = 125
```

The output from each process is prepended with the process's rank index.

### Part c

In [ex0-c-mpioptional.py](0-mpi-optional/ex0-c-mpioptional.py), we have an MPI-optional implementation of our example program. 
The implementation essentially treats the single non-mpi process as an mpi process with `rank == 0` of `size == 1`. 
The program checks for `comm == None` to distinguish between mpi and non-mpi code paths. 
The default execution does not use MPI. 

Run without using MPI:

```
> python ex0-c-mpioptional.py
0: Hello!
0: (0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
0: (0) subtotal = 45
0: (0) total = 45
0: (1) numbers = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
0: (1) subtotal = 145
0: (1) total = 145
0: (2) numbers = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
0: (2) subtotal = 245
0: (2) total = 245
```

Run using MPI:

```
> mpiexec -n 2 python ex0-c-mpioptional.py --mpi
1: Hello!
0: Hello!
0: (0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
0: (0) subtotal = 20
1: (0) subtotal = 25
0: (0) total = 45
0: (1) numbers = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
0: (1) subtotal = 70
1: (1) subtotal = 75
0: (1) total = 145
0: (2) numbers = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
0: (2) subtotal = 120
0: (2) total = 245
1: (2) subtotal = 125
```

### Part d

In certain circumstances, we'd like to be able to continue processing tasks after encountering an error in a preceding task. 
In [`ex0-d-trigger-errors.py`](0-mpi-optional/ex0-d-trigger-errors.py), we've injected errors into the example program that can be controlled with command line arguments. 
Play around with the `--trigger-one`, `--trigger-two`, and `--trigger-three` options without MPI and then try while using MPI. 
If you get stuck, try `CRTL-C` (press the `control`-key and the `c`-key at the same time).

```
> python ex0-d-trigger-errors.py --trigger-one
0: Hello!
0: (0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
0: (0) subtotal = 45
0: (0) total = 45
Traceback (most recent call last):
  File "ex0-d-trigger-errors.py", line 62, in <module>
    main()
  File "ex0-d-trigger-errors.py", line 32, in main
    raise RuntimeError(f"{rank}: error generating data!")
RuntimeError: 0: error generating data!
```

```
> mpiexec -n 2 python ex0-d-trigger-errors.py --mpi --trigger-one
0: Hello!
1: Hello!
0: (0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
0: (0) subtotal = 20
1: (0) subtotal = 25
0: (0) total = 45
Traceback (most recent call last):
  File "ex0-d-trigger-errors.py", line 62, in <module>
    main()
  File "ex0-d-trigger-errors.py", line 32, in main
    raise RuntimeError(f"{rank}: error generating data!")
RuntimeError: 0: error generating data!
^C
```

## 1. Exception Handling

When the MPI version of the example program encounters an error, the process that encounters the error exits but the other processes end up waiting at a collective communication event (bcast/gather/barrier/etc) indefinitely. 
In a batch job on an HPC system such as NERSC, this is bad because the job will sit until the job timelimit runs out. 
Sometimes we can ignore the error from a single task and we'd like our job to continue processing the remaining tasks. 
This section will demonstrate how to make our example program more robust for these situations.

### Part a

First attempt at catching errors: [`ex1-a-unsafe.py`](1-exception-handling/ex1-a-unsafe.py)

To run the non-mpi version:

```
> python ex1-a-unsafe.py
0: Hello!
0: (0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
0: (0) subtotal = 45
0: (0) total = 45
0: (1) numbers = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
0: (1) subtotal = 145
0: (1) total = 145
0: (2) numbers = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
0: (2) subtotal = 245
0: (2) total = 245
```

To run the mpi-enabled version:

```
> mpiexec -n 2 python ex1-a-unsafe.py --mpi
0: Hello!
1: Hello!
0: (0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
1: (0) subtotal = 25
0: (0) subtotal = 20
0: (0) total = 45
0: (1) numbers = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
0: (1) subtotal = 70
1: (1) subtotal = 75
0: (1) total = 145
0: (2) numbers = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
0: (2) subtotal = 120
1: (2) subtotal = 125
0: (2) total = 245
```

The `--trigger-one` option forces an error on rank 0 while generating the data during the second iteration. 
In the non-mpi version, the error is caught and the process skips to the next iteration:

```
> python ex1-a-unsafe.py --trigger-one
0: Hello!
0: (0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
0: (0) subtotal = 45
0: (0) total = 45
0: (1) skipping -> <class 'RuntimeError'> 0: error generating data!
0: (2) numbers = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
0: (2) subtotal = 245
0: (2) total = 245
```

However, the mpi version gets stuck and needs a `CRTL-C` to abort:

```
> mpiexec -n 2 python ex1-a-unsafe.py --trigger-one --mpi
0: Hello!
1: Hello!
0: (0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
0: (0) subtotal = 20
1: (0) subtotal = 25
1: (1) subtotal = 125
0: (0) total = 45
0: (1) skipping -> <class 'RuntimeError'> 0: error generating data!
0: (2) numbers = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
0: (2) subtotal = 120
0: (2) total = 245
^C
```

When the error is generated on rank 0 during the second iteration, it is caught on rank 0 and rank 0 moves onto the third iteration. 
rank 1 does not know about the error and is waiting at the broadcast step during the second iteration. 
When rank 0 moves on to third iteration, it generates the third dataset and broadcasts, which rank 1 picks up on its second iteration. 
rank 1 computes the subtotal using the data from the third iteration on its second iteration. 
rank 0, on its third iteration, eventually accepts the subtotal from rank 1 (computed on rank 1's second iteration using the data from the third iteration). 
rank 0 computes the combined total and has now reached the end of its process. 
Meanwhile, rank 1 moves on to its third iteration and gets stuck waiting at the broadcast step. A `CRTL-C` will come in handy at this point.

### Part b

One strategy to avoid getting stuck is to be more cautious before performing collective mpi communication. 
The example implementation in [`ex1-b-safe.py`](1-exception-handling/ex1-b-safe.py) attempts to catch and communicate errors when they occur in any single rank and so that they can be re-raised by all ranks.

Now we can can see that we successfully skip the problem task and the program does not get stuck:

```
> mpiexec -n 2 python ex1-b-safe.py --trigger-one --mpi
0: Hello!
1: Hello!
0: (0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
0: (0) subtotal = 20
1: (0) subtotal = 25
0: (0) total = 45
0: (1) skipping -> <class 'RuntimeError'> 0: caught error before bcast!
0: (2) numbers = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
1: (1) skipping -> <class 'RuntimeError'> 1: caught error before bcast!
0: (2) subtotal = 120
1: (2) subtotal = 125
0: (2) total = 245
```

### Part c

The example implementation in [`ex1-c-safe-again.py`](1-exception-handling/ex1-c-safe-again.py) uses a helper class to achieve to achieve the same effect. 
The helper classes in [`ex1helpers.py`](1-exception-handling/ex1helpers.py) allow for a less noisy main program and makes the pattern easier to reuse and extend.

```
> mpiexec -n 2 python ex1-c-safe-again.py --trigger-one --mpi
0: Hello!
1: Hello!
0: (0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
0: (0) subtotal = 20
1: (0) subtotal = 25
0: (0) total = 45
0: (1) skipping -> <class 'RuntimeError'> 0: caught error before bcast!
0: (2) numbers = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
0: (2) subtotal = 120
1: (1) skipping -> <class 'RuntimeError'> 1: caught error before bcast!
1: (2) subtotal = 125
0: (2) total = 245
```

The `--trigger-two` argument can be used to induce and error while one of the ranks is computing its subtotal before communicating back to the root rank. 

### 2. Async-IO

Insert async-io example description here.

### Part a

Use the `time` module to inject latency in our example program:

```
> python ex2-a-refactor.py
0: Hello!
0: (0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
0: (0) subtotal = 45
0: (0) total = 45
0: (1) numbers = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
0: (1) subtotal = 145
0: (1) total = 145
0: (2) numbers = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
0: (2) subtotal = 245
0: (2) total = 245
```

```
> mpiexec -n 2 ex2-a-refactor.py --mpi
1: Hello!
0: Hello!
0: (0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
0: (0) subtotal = 20
1: (0) subtotal = 25
0: (0) total = 45
0: (1) numbers = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
1: (1) subtotal = 75
0: (1) subtotal = 70
0: (1) total = 145
0: (2) numbers = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
1: (2) subtotal = 125
0: (2) subtotal = 120
0: (2) total = 245
```

### Part b

Parallel IO:

```
> python ex2-b-async.py
0: Hello!
0: (0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
0: (0) subtotal = 45
0: (0) total = 45
0: (1) numbers = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
0: (1) subtotal = 145
0: (1) total = 145
0: (2) numbers = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
0: (2) subtotal = 245
0: (2) total = 245
```

```
> mpiexec -n 2 python ex2-b-async.py --mpi
0: Hello!
1: Hello!
0: (0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
0: (0) subtotal = 20
1: (0) subtotal = 25
0: (0) total = 45
0: (1) numbers = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
0: (1) subtotal = 70
1: (1) subtotal = 75
0: (1) total = 145
0: (2) numbers = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
1: (2) subtotal = 125
0: (2) subtotal = 120
0: (2) total = 245
```

```
> mpiexec -n 4 python ex2-b-async.py --mpi --async-io
1: Hello!
0: Hello!
2: Hello!
3: Hello!
0: (0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
2: (0) subtotal = 20
3: (0) subtotal = 25
0: (1) numbers = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
1: (0) total = 45
2: (1) subtotal = 70
3: (1) subtotal = 75
0: (2) numbers = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
2: (2) subtotal = 120
3: (2) subtotal = 125
1: (1) total = 145
1: (2) total = 245
```

### Part c

Parallel IO with helpers:

```
> python ex2-c-async-again.py
0: Hello!
0: (0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
0: (0) subtotal = 45
0: (0) total = 45
0: (1) numbers = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
0: (1) subtotal = 145
0: (1) total = 145
0: (2) numbers = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
0: (2) subtotal = 245
0: (2) total = 245
```

```
> mpiexec -n 2 python ex2-c-async-again.py --mpi
1: Hello!
0: Hello!
0: (0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
0: (0) subtotal = 20
1: (0) subtotal = 25
0: (0) total = 45
0: (1) numbers = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
0: (1) subtotal = 70
1: (1) subtotal = 75
0: (1) total = 145
0: (2) numbers = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
0: (2) subtotal = 120
1: (2) subtotal = 125
0: (2) total = 245
```

```
> mpiexec -n 4 python ex2-c-async-again.py --mpi --async-io
0: Hello!
1: Hello!
2: Hello!
3: Hello!
0: (0) numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
2: (0) subtotal = 20
3: (0) subtotal = 25
0: (1) numbers = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
1: (0) total = 45
2: (1) subtotal = 70
3: (1) subtotal = 75
0: (2) numbers = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
2: (2) subtotal = 120
3: (2) subtotal = 125
1: (1) total = 145
1: (2) total = 245
```

### 3. Combined (Exception Handling + Async-IO)

Insert combination of exception handling pattern and async-io pattern here.

## References

Also, checkout mpi4py.run as a potential alternative:
 * https://mpi4py.readthedocs.io/en/stable/mpi4py.run.html


