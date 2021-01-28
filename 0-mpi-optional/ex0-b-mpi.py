#!/usr/bin/env python

def main():

    # mpi setup
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    rank, size = comm.rank, comm.size

    # say hello
    print(f"{rank}: Hello!")
    comm.barrier()

    # iterate over tasks
    for i in range(3):

        # generate data
        numbers = None
        if rank == 0:
            numbers = list(range(i*10, (i+1)*10))
            print(f"{rank}: ({i}) numbers = {numbers}")

        # broadcast data
        numbers = comm.bcast(numbers, root=0)

        # each rank computes a subtotal
        subtotal = 0
        for value in numbers[rank::size]:
            subtotal += value
        print(f"{rank}: ({i}) subtotal = {subtotal}")

        # gather subtotals
        subtotals = comm.gather(subtotal, root=0)

        # sum subtotals and print result
        if rank == 0:
            total = sum(subtotals)
            print(f"{rank}: ({i}) total = {total}")


if __name__ == "__main__":
    main()
