#!/usr/bin/env python

import argparse

from helpers import (
    MyModule,
    NoMPIIOComm,
    SyncIOComm,
    AsyncIOComm,
    NoMPIComm,
    SafeMPIComm,
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

        try:
            mymod = MyModule(rank, size, i, args)

            # generate data
            numbers = comm.read(lambda: mymod.load_data(10), None)

            subtotals = None
            if comm.is_worker():

                if comm.work_comm is not None:
                    work_comm = SafeMPIComm(comm.work_comm)
                else:
                    work_comm = NoMPIComm()

                # broadcast data
                # note: this is essentially a less efficient way to mpi scatter
                numbers = work_comm.bcast(lambda: numbers, root=0)
                numbers = numbers[work_comm.rank::work_comm.size]

                # gather subtotals
                error = None
                try:
                    # each rank computes a subtotal
                    subtotals = work_comm.gather(
                        lambda: mymod.process_data(numbers), root=0
                    )
                except Exception as e:
                    # workers catch the error here so worker_root can send to write_rank
                    error = e
                
                # send the error to write rank before it tries to write anything
                if comm.is_worker_root() and isinstance(comm, AsyncIOComm):
                    comm.comm.send(error, comm.WRITE_RANK, tag=0)

                # workers re-raise error here
                if error is not None:
                    raise error

            # sum subtotals and print result
            comm.write(
                lambda result: mymod.write_result(result), subtotals
            )

        except Exception as e:
            print(f"{rank}: ({i}) skipping -> {type(e)} {e}")
            continue

    if comm.comm is not None:
        comm.comm.barrier()


if __name__ == "__main__":
    main()
