# mpi-playground

Examples of using mpi4py with exception handling and async-io patterns.

## Example 0

Insert mpi-optional pattern description here.

## Example 1

### Part a

`ex1-a-unsafe.py` is an example use case implemented with typical mpi-optional pattern. 

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

The implementation essentially treats the single non-mpi process as an mpi process with `rank == 0` of `size == 1`. The program checks for `comm == None` to distinguish between mpi and non-mpi code paths.

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

In the mpi version, each rank computes an independent subtotal which are then combined into a single total by rank 0.

The `--trigger-one` option forces an error on rank 0 while generating the data during the second iteration. In the non-mpi version, the error is caught and the process skips to the next iteration:

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

When the error is generated on rank 0 during the second iteration, it is caught on rank 0 and rank 0 moves onto the third iteration. rank 1 does not know about the error and is waiting at the broadcast step during the second iteration. When rank 0 moves on to third iteration, it generates the third dataset and broadcasts, which rank 1 picks up on its second iteration. rank 1 computes the subtotal using the data from the third iteration on its second iteration. rank 0, on its third iteration, eventually accepts the subtotal from rank 1 (computed on rank 1's second iteration using the data from the third iteration). rank 0 computes the combined total and has now reached the end of its process. Meanwhile, rank 1 moves on to its third iteration and gets stuck waiting at the broadcast step. A `CRTL-C` will come in handy at this point.

### Part b

One strategy to avoid getting stuck is to be more cautious before performing collective mpi communication. The example implementation in `ex2-safe.py` tries to catch and communicate errors when they occur in any single rank and so that they can be re-raised by all ranks.

The following shows what happens when we try `ex2-safe.py` with the `--trigger-one` option.

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

The example implementation in `ex3-safe-again.py` uses a helper class to achieve to achieve the same effect. The helper classes in `safety.py` allow for a less noisy main program and makes the pattern easy to reuse and extend.

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

### Example 2

Insert async-io example description here.

### Example 3

Insert combination of exception handling pattern and async-io pattern here.

## References

Also, checkout mpi4py.run as a potential alternative:
 * https://mpi4py.readthedocs.io/en/stable/mpi4py.run.html


