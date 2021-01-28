#!/usr/bin/env python

import argparse

from helpers import MyModule

def main():

    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--mpi", action="store_true", help="use mpi")
    parser.add_argument("--trigger-one", action="store_true", help="raise error")
    parser.add_argument("--trigger-two", action="store_true", help="raise error")
    parser.add_argument("--trigger-three", action="store_true", help="raise error")
    parser.add_argument("--async-io", action="store_true", help="async io")
    args = parser.parse_args()

    if args.mpi:
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank, size = comm.rank, comm.size
        if args.async_io:
            READ_RANK, WRITE_RANK, WORK_ROOT = 0, 1, 2
            work_comm = None
            work_group = comm.group.Excl([READ_RANK, WRITE_RANK])
            if rank not in [READ_RANK, WRITE_RANK]:
                work_comm = comm.Create_group(work_group)
        else:
            READ_RANK, WRITE_RANK, WORK_ROOT = 0, 0, 0
            work_comm = comm
    else:
        comm = None
        rank, size = 0, 1
        READ_RANK, WRITE_RANK, WORK_ROOT = 0, 0, 0
        work_comm = None

    def say_hello():
        print(f"{rank}: Hello!")

    # synch comm group after saying hello
    # comm.comm.barrier(say_hello)

    for i in range(3):
        try:
            mymod = MyModule(rank, size, i, args)

            # try to generate data on rank 0
            numbers = None
            if rank == READ_RANK:
                numbers = mymod.load_data(10)

            if args.async_io:
                if rank == READ_RANK:
                    comm.send(numbers, dest=WORK_ROOT)
                elif rank == WORK_ROOT:
                    numbers = comm.recv(source=READ_RANK)

            subtotals = None
            if rank >= WORK_ROOT:

                # broadcast data
                if work_comm is not None:
                    numbers = work_comm.bcast(numbers, root=0)
                    numbers = numbers[work_comm.rank::work_comm.size]
                
                subtotal = mymod.process_data(numbers)

                # gather subtotals
                if work_comm is not None:
                    subtotals = work_comm.gather(subtotal, root=0)
                else:
                    subtotals = [subtotal, ]

            if args.async_io:
                if rank == WORK_ROOT:
                    comm.send(subtotals, dest=WRITE_RANK)
                elif rank == WRITE_RANK:
                    subtotals = comm.recv(source=WORK_ROOT)

            if rank == WRITE_RANK:
                mymod.write_result(subtotals)

        except Exception as e:
            print(f"{rank}: ({i}) skipping -> {type(e)} {e}")
            continue


if __name__ == "__main__":
    main()
