#!/usr/bin/env python

import argparse

from helpers import MyModule

def main():

    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--mpi", action="store_true", help="use mpi")
    parser.add_argument("--trigger-one", action="store_true", help="raise error")
    parser.add_argument("--trigger-two", action="store_true", help="raise error")
    parser.add_argument("--trigger-three", action="store_true", help="raise error")
    args = parser.parse_args()

    # optional mpi setup
    if args.mpi:
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank, size = comm.rank, comm.size
    else:
        comm = None
        rank, size = 0, 1

    # say hello
    print(f"{rank}: Hello!")
    if comm is not None:
        comm.barrier()

    # iterate over tasks
    for i in range(3):

        mymod = MyModule(rank, size, i, args)

        # generate data
        numbers = None
        if rank == 0:
            numbers = mymod.load_data(10)

        # broadcast data
        if comm is not None:
            numbers = comm.bcast(numbers, root=0)
            
        # each rank computes a subtotal
        subtotal = mymod.process_data(numbers[rank::size])

        # gather subtotals
        if comm is not None:
            subtotals = comm.gather(subtotal, root=0)
        else:
            subtotals = [subtotal, ]

        # sum subtotals and print result
        if rank == 0:
            mymod.write_result(subtotals)

    if comm is not None:
        comm.barrier()


if __name__ == "__main__":
    main()
