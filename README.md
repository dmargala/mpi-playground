# mpi4dummies

Examples of mpi4py + exception handling.

## Examples

### Example 1

`ex1-unsafe.py` is an example of an mpi-optional implementation. The implementation essentially treats the single non-mpi process as an mpi process with `rank == 0` of `size == 1`. The program checks for `comm == None` to distinguish between mpi and non-mpi code paths.

To run the non-mpi version:

```
> python ex1-unsafe.py 
0: Hello!
0: (0) subtotal = 45
0: (0) total = 45
0: (1) subtotal = 190
0: (1) total = 190
0: (2) subtotal = 435
0: (2) total = 435
```

To run the mpi-enabled version:

```
> mpiexec -n 2 python ex1-unsafe.py --mpi
0: Hello!
1: Hello!
0: (0) subtotal = 20
1: (0) subtotal = 25
0: (0) total = 45
1: (1) subtotal = 100
0: (1) subtotal = 90
0: (1) total = 190
1: (2) subtotal = 225
0: (2) subtotal = 210
0: (2) total = 435
```

In the mpi version, each rank is computing a subtotal and those are combined into a single total which is reported by rank 0.

We can force an error to occur while generating data during the second iteration using the `--trigger-one` option. In the non-mpi version, the error is caught and the process skips to the next iteration:

```
> python ex1-unsafe.py --trigger-one
0: Hello!
0: (0) subtotal = 45
0: (0) total = 45
0: (1) skipping -> <class 'RuntimeError'> 0: error generating data!
0: (2) subtotal = 435
0: (2) total = 435
```

However, the mpi version gets stuck and needs a `CRTL-C` to abort:

```
> mpiexec -n 2 python ex1-unsafe.py --trigger-one --mpi
1: Hello!
0: Hello!
0: (0) subtotal = 20
1: (0) subtotal = 25
0: (0) total = 45
0: (1) skipping -> <class 'RuntimeError'> 0: error generating data!
1: (1) subtotal = 225
0: (2) subtotal = 210
0: (2) total = 435
^C
```

### Example 2

One strategy to avoid getting stuck is to be more cautious before performing collective mpi communication. `ex2-safe.py` is an example implementation tries to catch errors when they occur in a single rank and broadcast/gatherall so that they are re-raised by all ranks.

The following shows what happens when we try `ex2-safe.py` with the `--trigger-one` option.

```
> mpiexec -n 2 python ex2-safe.py --trigger-one --mpi
0: Hello!
1: Hello!
0: (0) subtotal = 20
1: (0) subtotal = 25
0: (0) total = 45
0: (1) skipping -> <class 'RuntimeError'> 0: caught error before bcast!
1: (1) skipping -> <class 'RuntimeError'> 1: caught error before bcast!
0: (2) subtotal = 210
1: (2) subtotal = 225
0: (2) total = 435
```

### Example 3

`ex3-mpi4dummies.py` is an example that uses the helper classes to achieve the same thing. The implementation is a bit cleaner and makes the pattern easy to reuse and extend.

```
> mpiexec -n 2 python ex3-mpi4dummies.py --trigger-one --mpi
0: Hello!
1: Hello!
0: (0) subtotal = 20
1: (0) subtotal = 25
0: (0) total = 45
0: (1) skipping -> <class 'RuntimeError'> 0: caught error before bcast!
1: (1) skipping -> <class 'RuntimeError'> 1: caught error before bcast!
0: (2) subtotal = 210
1: (2) subtotal = 225
0: (2) total = 435
```

The `--trigger-two` argument can be used to induce and error at a different stage in the typical use case.


## References

Also, checkout mpi4py.run as a potential alternative:
 * https://mpi4py.readthedocs.io/en/stable/mpi4py.run.html


