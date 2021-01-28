#!/usr/bin/env python

import argparse

from helpers import (
    MyModule,
    NoMPIIOComm,
    SyncIOComm,
    AsyncIOComm,
)

def main():

    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--mpi", action="store_true", help="use mpi")
    parser.add_argument("--trigger-one", action="store_true", help="raise error")
    parser.add_argument("--trigger-two", action="store_true", help="raise error")
    parser.add_argument("--trigger-three", action="store_true", help="raise error")
    parser.add_argument("--async-io", action="store_true", help="async io")
    args = parser.parse_args()

    # optional mpi setup
    if args.mpi:
        from mpi4py import MPI
        if args.async_io:
            comm = AsyncIOComm(MPI.COMM_WORLD)
        else:
            comm = SyncIOComm(MPI.COMM_WORLD)
    else:
        comm = NoMPIIOComm()

    rank, size = comm.rank, comm.size

    # say hello
    print(f"{rank}: Hello!")
    if comm.comm is not None:
        comm.comm.barrier()

    # iterate over tasks
    for i in range(3):

        mymod = MyModule(rank, size, i, args)

        # generate data
        numbers = comm.read(lambda: mymod.load_data(10), None)

        subtotals = None
        if comm.is_worker():

            # broadcast data
            if comm.work_comm is not None:
                numbers = comm.work_comm.bcast(numbers, root=0)
                numbers = numbers[comm.work_comm.rank::comm.work_comm.size]

            # each rank computes a subtotal
            subtotal = mymod.process_data(numbers)

            # gather subtotals
            if comm.work_comm is not None:
                subtotals = comm.work_comm.gather(subtotal, root=0)
            else:
                subtotals = [subtotal, ]

        # sum subtotals and print result
        comm.write(lambda r: mymod.write_result(r), subtotals)

    if comm.comm is not None:
        comm.comm.barrier()


if __name__ == "__main__":
    main()
