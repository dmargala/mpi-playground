#!/usr/bin/env python

import argparse

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
        
        try:
            # generate data
            numbers = None
            if rank == 0:
                if args.trigger_one and i == 1:
                    raise RuntimeError(f"{rank}: error generating data!")
                numbers = list(range(i*10, (i+1)*10))
                print(f"{rank}: ({i}) numbers = {numbers}")

            # broadcast data
            if comm is not None:
                numbers = comm.bcast(numbers, root=0)

            # each rank computes a subtotal
            if rank == size - 1:
                if args.trigger_two and i == 1:
                    raise RuntimeError(f"{rank}: error performing work!")
            subtotal = 0
            for value in numbers[rank::size]:
                subtotal += value
            print(f"{rank}: ({i}) subtotal = {subtotal}")

            # gather subtotals
            if comm is not None:
                subtotals = comm.gather(subtotal, root=0)
            else:
                subtotals = [subtotal, ]

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
