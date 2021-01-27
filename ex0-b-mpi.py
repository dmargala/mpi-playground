#!/usr/bin/env python

def main():

    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    rank, size = comm.rank, comm.size

    # say hello
    print(f"{rank}: Hello!")
    comm.barrier()

    for i in range(3):
        # try to generate data on rank 0
        data = None
        if rank == 0:
            data = list(range((i+1)*10))

        # broadcast data
        data = comm.bcast(data, root=0)

        # each rank computes a subtotal
        subtotal = 0
        for value in data[rank::size]:
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
