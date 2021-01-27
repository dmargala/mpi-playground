#!/usr/bin/env python

import argparse
import time

class MyModule(object):
    def __init__(self, rank, size, index, args):
        self.rank = rank
        self.size = size
        self.index = index
        self.trigger_one = args.trigger_one
        self.trigger_two = args.trigger_two
        self.trigger_three = args.trigger_three

    def msg(self, s):
        return f"{self.rank}: ({self.index}) {s}"

    def load_data(self, n):
        time.sleep(0.5)
        if self.trigger_one and self.index == 1:
            raise RuntimeError(self.msg(f"error during load_data!"))
        numbers = list(range((self.index*n), (self.index+1)*n))
        print(self.msg(f"numbers = {numbers}"))
        return numbers

    def process_data(self, numbers):
        if self.trigger_two and self.index == 1:
            if self.rank == self.size - 1:
                raise RuntimeError(self.msg(f"error during process_data!"))
        subtotal = 0
        for value in numbers:
            time.sleep(0.05)
            subtotal += value
        print(self.msg(f"subtotal = {subtotal}"))
        return subtotal

    def write_result(self, subtotals):
        time.sleep(0.5)
        if self.trigger_three and self.index == 1:
            raise RuntimeError(self.msg(f"error during write_result!"))
        # sum subtotals and print result
        total = sum(subtotals)
        print(self.msg(f"total = {total}"))

def main():

    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--mpi", action="store_true", help="use mpi")
    parser.add_argument("--trigger-one", action="store_true", help="raise error")
    parser.add_argument("--trigger-two", action="store_true", help="raise error")
    parser.add_argument("--trigger-three", action="store_true", help="raise error")
    args = parser.parse_args()

    if args.mpi:
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank, size = comm.rank, comm.size
    else:
        comm = None
        rank, size = 0, 1

    def say_hello():
        print(f"{rank}: Hello!")

    # synch comm group after saying hello
    # comm.comm.barrier(say_hello)

    for i in range(3):
        try:
            mymod = MyModule(rank, size, i, args)

            # try to generate data on rank 0
            numbers = None
            if rank == 0:
                numbers = mymod.load_data(10)

            # broadcast data
            if comm is not None:
                numbers = comm.bcast(numbers, root=0)
                
            # each rank computes a subtotal
            subtotal = mymod.process_data(numbers[rank::size])

            # gather subtotals
            if comm is not None:
                subtotals = comm.gather(subtotal, root=0)
            else:
                subtotals = [subtotal, ]

            # sum subtotals and print result
            if rank == 0:
                mymod.write_result(subtotals)

        except Exception as e:
            print(f"{rank}: ({i}) skipping -> {type(e)} {e}")
            continue


if __name__ == "__main__":
    main()
