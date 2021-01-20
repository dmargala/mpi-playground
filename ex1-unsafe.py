#!/usr/bin/env python

import argparse

def main():

    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--mpi", action="store_true", help="use mpi")
    parser.add_argument("--trigger-one", action="store_true", help="raise error")
    parser.add_argument("--trigger-two", action="store_true", help="raise error")
    args = parser.parse_args()

    if args.mpi:
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank, size = comm.rank, comm.size
    else:
        comm = None
        rank, size = 0, 1

    print(f"{rank}: Hello!")

    # synch comm group after saying hello
    if comm is not None:
        comm.barrier()

    for i in range(3):
        try:
            # try to generate data on rank 0
            data = None
            if rank == 0:
                if args.trigger_one and i == 1:
                    raise RuntimeError(f"{rank}: error generating data!")
                data = list(range((i+1)*10))

            # broadcast data
            if comm is not None:
                data = comm.bcast(data, root=0)

            # each rank computes a subtotal
            if rank == size - 1:
                if args.trigger_two and i == 1:
                    raise RuntimeError(f"{rank}: error performing work!")
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

        except Exception as e:
            print(f"{rank}: ({i}) skipping -> {type(e)} {e}")
            continue


if __name__ == "__main__":
    main()
