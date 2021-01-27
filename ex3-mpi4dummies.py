#!/usr/bin/env python

import argparse

from mpi4dummies import NoMPIComm, SafeMPIComm

def main():

    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--mpi", action="store_true", help="use mpi")
    parser.add_argument("--trigger-one", action="store_true", help="raise error")
    parser.add_argument("--trigger-two", action="store_true", help="raise error")
    parser.add_argument("--trigger-three", action="store_true", help="raise error")
    args = parser.parse_args()

    if args.mpi:
        from mpi4py import MPI
        comm = SafeMPIComm(MPI.COMM_WORLD)
    else:
        comm = NoMPIComm()

    rank, size = comm.rank, comm.size

    def say_hello():
        print(f"{rank}: Hello!")

    # synch comm group after saying hello
    comm.barrier(say_hello)

    for i in range(3):
        try:
            # try to generate data on rank 0
            def rootfunc():
                if args.trigger_one and i == 1:
                    raise RuntimeError(f"{rank}: error generating data!")
                return list(range((i+1)*10))

            # broadcast data
            data = comm.bcast(rootfunc, root=0)

            # each rank computes a subtotal
            def rankfunc():
                if rank == size - 1:
                    if args.trigger_two and i == 1:
                        raise RuntimeError(f"{rank}: error performing work!")
                subtotal = 0
                for value in data[rank::size]:
                    subtotal += value
                print(f"{rank}: ({i}) subtotal = {subtotal}")
                return subtotal

            # gather subtotals
            subtotals = comm.gather(rankfunc, root=0)

            # sum subtotals and print result
            if rank == 0:
                if args.trigger_three and i == 1:
                    raise RuntimeError(f"{rank}: error printing result!")
                total = sum(subtotals)
                print(f"{rank}: ({i}) total = {total}")

        except Exception as e:
            print(f"{rank}: ({i}) skipping -> {type(e)} {e}")
            continue


if __name__ == "__main__":
    main()
