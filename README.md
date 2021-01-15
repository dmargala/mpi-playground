# mpi4dummies

Examples of mpi4py + exception handling.

## Examples

`ex1-unsafe.py` represents a typical mpi4py optional use case.

```
> python ex1-unsafe.py 
0: Hello!
0: [123]
0: [1230]
0: [12300]
```

And the mpi version:

```
> mpiexec -n 2 python ex1-unsafe.py --mpi
0: Hello!
1: Hello!
0: [123, 124]
0: [1230, 1231]
0: [12300, 12301]
```

We can force an error to occur using `--trigger-one` during the second iteration, the error is caught, and the process continues:

```
> python ex1-unsafe.py --trigger-one
0: Hello!
0: [123]
0: skipping iteration 1: <class 'RuntimeError'> 0: error setting value!
0: [12300]
```

However, trigger the error using the mpi version, the process gets stuck and needs a `CRTL-C` to abort:

```
> mpiexec -n 2 python ex1-unsafe.py --trigger-one --mpi
1: Hello!
0: Hello!
0: [123, 124]
0: skipping iteration 1: <class 'RuntimeError'> 0: error setting value!
0: [12300, 12301]
^C
```

`ex2-safe.py` is an example of being a little more cautious before performing collective mpi communication:

```
> mpiexec -n 2 python ex2-safe.py --trigger-one --mpi
0: Hello!
1: Hello!
0: [123, 124]
1: skipping iteration 1: <class 'RuntimeError'> 1: caught error before collective comm!
0: skipping iteration 1: <class 'RuntimeError'> 0: caught error before collective comm!
0: [12300, 12301]
```

`ex3-mpi4dummies.py` is an example that uses the helper classes to achieve the same thing and has a maybe a bit cleaner implementation overall:

```
> mpiexec -n 2 python ex3-mpi4dummies.py --trigger-one --mpi
0: Hello!
1: Hello!
0: [123, 124]
0: skipping iteration 1: <class 'RuntimeError'> 0: caught error before collective comm!
1: skipping iteration 1: <class 'RuntimeError'> 1: caught error before collective comm!
0: [12300, 12301]
```

The `--trigger-two` argument can be used to induce and error at a different stage in the typical use case.


## References

Also, checkout mpi4py.run as a potential alternative:
    * https://mpi4py.readthedocs.io/en/stable/mpi4py.run.html


