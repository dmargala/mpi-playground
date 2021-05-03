#!/usr/bin/env python

import argparse

from helpers import Task


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

    # say hello
    print(f"{rank}: Hello!")
    if comm is not None:
        comm.barrier()

    # iterate over tasks
    for i in range(3):

        task = Task(rank, size, i, args)

        # generate data
        numbers = None
        if rank == READ_RANK:
            numbers = task.load_data(10)

        if args.async_io:
            if rank == READ_RANK:
                comm.send(numbers, dest=WORK_ROOT)
            elif rank == WORK_ROOT:
                numbers = comm.recv(source=READ_RANK)

        # divide work between ranks and gather result on root
        subtotals = None
        if rank >= WORK_ROOT:
            subtotals = task.divide_and_conquer(numbers, work_comm)

        if args.async_io:
            if rank == WORK_ROOT:
                comm.send(subtotals, dest=WRITE_RANK)
            elif rank == WRITE_RANK:
                subtotals = comm.recv(source=WORK_ROOT)

        # sum subtotals and print result
        if rank == WRITE_RANK:
            task.write_result(subtotals)

    if comm is not None:
        comm.barrier()


if __name__ == "__main__":
    main()
