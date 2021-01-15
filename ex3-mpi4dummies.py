#!/usr/bin/env python

import argparse

from mpi4dummies import NoMPIComm, SafeMPIComm

def main():

    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--mpi", action="store_true", help="use mpi")
    parser.add_argument("--trigger-one", action="store_true", help="raise error")
    parser.add_argument("--trigger-two", action="store_true", help="raise error")
    args = parser.parse_args()

    if args.mpi:
        from mpi4py import MPI
        comm = SafeMPIComm(MPI.COMM_WORLD)
    else:
        comm = NoMPIComm()

    rank, size = comm.rank, comm.size

    print(f"{rank}: Hello!")

    for i in range(3):
        try:
            # Try to set a value on rank 0
            def rootfunc():
                if args.trigger_one and i == 1:
                    raise RuntimeError(f"{rank}: error setting value!")
                return 123 * (10**i)

            # broadcast value
            value = comm.bcast(rootfunc, root=0)

            # Each rank do something with value
            def rankfunc():
                if rank == size - 1 and i == 1:
                    if args.trigger_two:
                        raise RuntimeError(f"{rank}: error using value!")
                return value + rank

            # gather values
            values = comm.gather(rankfunc, root=0)

            # print combined result
            if rank == 0:
                print(f"{rank}: {values}")
        except Exception as e:
            print(f"{rank}: skipping iteration {i}: {type(e)} {e}")
            continue


if __name__ == "__main__":
    main()
