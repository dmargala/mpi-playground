#!/usr/bin/env python

import argparse
import time

class NoMPIIOComm(object):
    READ_RANK = 0
    WRITE_RANK = 0
    WORK_ROOT = 0

    def __init__(self):
        self.comm = None
        self.rank = 0
        self.size = 1

        self.work_comm = None

    def is_worker(self):
        return True

    def is_worker_root(self):
        return True

    def read(self, func, data):
        return func()

    def write(self, func, data):
        func(data)

class SyncIOComm(object):
    READ_RANK = 0
    WRITE_RANK = 0
    WORK_ROOT = 0

    def __init__(self, comm):
        """Synchronous communication manager.

        Args:
            comm: the parent MPI communicator. Must have at least 1 rank
        """
        self.comm = comm
        self.rank = comm.rank
        self.size = comm.size

        self.work_comm = comm

    def is_worker(self):
        return self.comm.rank >= SyncIOComm.WORK_ROOT

    def is_worker_root(self):
        return self.comm.rank == SyncIOComm.WORK_ROOT

    def read(self, func, data):
        if self.comm.rank == SyncIOComm.READ_RANK:
            data = func()
        return data

    def write(self, func, data):
        if self.comm.rank == SyncIOComm.WRITE_RANK:
            func(data)

class AsyncIOComm(object):
    READ_RANK = 0
    WRITE_RANK = 1
    WORK_ROOT = 2

    def __init__(self, comm):
        """Asynchronous communication manager.

        Args:
            comm: the parent MPI communicator. Must have at least 3 ranks
        """
        self.comm = comm
        self.rank = comm.rank
        self.size = comm.size
        assert self.size >= 3

        # Initialize extraction comm
        # should READ/WRITE ranks have work_comm = MPI.COMM_NULL?
        self.work_comm = None
        self.work_group = self.comm.group.Excl(
            [AsyncIOComm.READ_RANK, AsyncIOComm.WRITE_RANK])
        if self.is_worker():
            self.work_comm = comm.Create_group(self.work_group)

    def is_worker(self):
        """Returns True if this MPI rank is part of the extraction group.
        Otherwise returns False.
        """
        return self.comm.rank >= AsyncIOComm.WORK_ROOT

    def is_worker_root(self):
        return self.comm.rank == AsyncIOComm.WORK_ROOT

    def read(self, func, data):
        """READ_RANK will call `func` and send the result to WORK_ROOT.
        WORK_ROOT returns the result from READ_RANK. All other ranks return 
        the provided default `data`.

        Args:
            func (method): function to be called by READ_RANK that reads input data.
            data: default placeholder for data. mostly here for symmetry with `write(...)`

        Returns: 
            data: either the provided default data or data returned by func on WORK_ROOT/READ_RANK
        """
        if self.comm.rank == AsyncIOComm.READ_RANK:
            data = func()
            self.comm.send(data, dest=AsyncIOComm.WORK_ROOT, tag=1)
        elif self.comm.rank == AsyncIOComm.WORK_ROOT:
            data = self.comm.recv(source=AsyncIOComm.READ_RANK, tag=1)
        return data

    def write(self, func, data):
        """WORK_ROOT sends `data` to WRITE_RANK. WRITE_RANK calls `func` to
        write `data`. This is a no-op for all other ranks.

        Args:
            func (method): function that writes `data`.
            data: the data to be written by `func`.
        """
        if self.comm.rank == AsyncIOComm.WORK_ROOT:
            self.comm.send(data, dest=AsyncIOComm.WRITE_RANK, tag=2)
        elif self.comm.rank == AsyncIOComm.WRITE_RANK:
            data = self.comm.recv(source=AsyncIOComm.WORK_ROOT, tag=2)
            func(data)


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
        if args.async_io:
            comm = AsyncIOComm(MPI.COMM_WORLD)
        else:
            comm = SyncIOComm(MPI.COMM_WORLD)
    else:
        comm = NoMPIIOComm()

    rank, size = comm.rank, comm.size

    def say_hello():
        print(f"{rank}: Hello!")

    # synch comm group after saying hello
    # comm.comm.barrier(say_hello)

    for i in range(3):
        try:
            def read():
                time.sleep(0.5)
                if args.trigger_one and i == 1:
                    raise RuntimeError(f"{rank}: error generating data!")
                # try to generate data on rank 0
                numbers = list(range(i*10, (i+1)*10))
                print(f"{rank}: ({i}) numbers = {numbers}")
                return numbers

            numbers = comm.read(read, None)

            subtotals = None

            if comm.is_worker():

                # broadcast data
                if comm.work_comm is not None:
                    numbers = comm.work_comm.bcast(numbers, root=0)

                    numbers = numbers[comm.work_comm.rank::comm.work_comm.size]

                # each rank computes a subtotal
                def work():
                    if rank == size - 1:
                        if args.trigger_two and i == 1:
                            raise RuntimeError(f"{rank}: error performing work!")
                    subtotal = 0
                    for value in numbers:
                        time.sleep(0.05)
                        subtotal += value
                    print(f"{rank}: ({i}) subtotal = {subtotal}")
                    return subtotal

                # gather subtotals
                if comm.work_comm is not None:
                    subtotals = comm.work_comm.gather(work(), root=0)
                else:
                    subtotals = [work()]

            def write(subtotals):
                time.sleep(0.5)
                if args.trigger_three and i == 1:
                    raise RuntimeError(f"{rank}: error writing result!")
                # sum subtotals and print result
                total = sum(subtotals)
                print(f"{rank}: ({i}) total = {total}")

            comm.write(write, subtotals)
        except Exception as e:
            print(f"{rank}: ({i}) skipping -> {type(e)} {e}")
            continue


if __name__ == "__main__":
    main()
