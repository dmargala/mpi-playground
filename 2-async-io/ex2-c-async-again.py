#!/usr/bin/env python

import argparse

from helpers import (
    Task,
    NoMPIIOCoordinator,
    SerialIOCoordinator,
    ParallelIOCoordinator,
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
            coordinator = ParallelIOCoordinator(MPI.COMM_WORLD)
        else:
            coordinator = SerialIOCoordinator(MPI.COMM_WORLD)
    else:
        coordinator = NoMPIIOCoordinator()
    rank, size = coordinator.rank, coordinator.size

    # say hello
    print(f"{rank}: Hello!")
    if coordinator.comm is not None:
        coordinator.comm.barrier()

    # iterate over tasks
    for i in range(3):
        task = Task(rank, size, i, args)
        # generate data
        numbers = coordinator.read(lambda: task.load_data(10), None)
        # divide work between ranks and gather result on root
        subtotals = coordinator.process(
            lambda: task.divide_and_conquer(numbers, coordinator.work_comm), None
        )
        # sum subtotals and print result
        coordinator.write(lambda r: task.write_result(r), subtotals)

    if coordinator.comm is not None:
        coordinator.comm.barrier()


if __name__ == "__main__":
    main()
