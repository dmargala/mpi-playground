#!/usr/bin/env python

import argparse

def main():

    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--mpi", action="store_true", help="use mpi")
    args = parser.parse_args()

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

    for i in range(3):
        # try to generate data on rank 0
        data = None
        if rank == 0:
            data = list(range((i+1)*10))

        # broadcast data
        if comm is not None:
            data = comm.bcast(data, root=0)

        # each rank computes a subtotal
        subtotal = 0
        for value in data[rank::size]:
            subtotal += value
        print(f"{rank}: ({i}) subtotal = {subtotal}")

        # gather subtotals
        if comm is not None:
            subtotals = comm.gather(subtotal, root=0)
        else:
            subtotals = [subtotal, ]

        # sum subtotals and print result
        if rank == 0:
            total = sum(subtotals)
            print(f"{rank}: ({i}) total = {total}")



if __name__ == "__main__":
    main()