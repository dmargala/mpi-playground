#!/usr/bin/env python

import argparse
import time

from asyncio import (
    NoMPIIOComm,
    SyncIOComm,
    AsyncIOComm,
)

from safety import (
    NoMPIComm,
    SafeMPIComm
)

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
            def load_data():
                time.sleep(0.5)
                if args.trigger_one and i == 1:
                    raise RuntimeError(f"{rank}: error generating data!")
                # try to generate data on rank 0
                numbers = list(range(i*10, (i+1)*10))
                print(f"{rank}: ({i}) numbers = {numbers}")
                return numbers

            numbers = comm.read(load_data, None)

            subtotals = None

            if comm.is_worker():

                if comm.work_comm is not None:
                    work_comm = SafeMPIComm(comm.work_comm)
                else:
                    work_comm = NoMPIComm()

                # broadcast data
                numbers = work_comm.bcast(lambda: numbers, root=0)
                numbers = numbers[work_comm.rank::work_comm.size]

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
                error = None
                try:
                    subtotals = work_comm.gather(work, root=0)
                except Exception as e:
                    error = e
                    
                if comm.is_worker_root() and isinstance(comm, AsyncIOComm):
                    comm.comm.send(error, comm.WRITE_RANK, tag=0)

                if error is not None:
                    raise error

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
