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

    for i in range(3):
        try:
            # Try to set a value on rank 0
            error = None
            value = None
            try:
                if rank == 0:
                    if args.trigger_one and i == 1:
                        raise RuntimeError(f"{rank}: error setting value!")
                    value = 123 * (10**i)
            except Exception as e:
                error = e

            # check for error
            if comm is not None:
                error = comm.bcast(error, root=0)
            if error is not None:
                # handle the error on all ranks
                msg = f"{rank}: caught error before collective comm!"
                raise RuntimeError(msg) from error

            # broadcast value
            if comm is not None:
                value = comm.bcast(value, root=0)

            # Each rank do something with value
            error = None
            try:
                if rank == size - 1:
                    if args.trigger_two and i == 1:
                        raise RuntimeError(f"{rank}: error using value!")
                new_value = value + rank
            except Exception as e:
                # only ranks with an error catch here
                error = e

            # check for error
            if comm is not None:
                errors = comm.allgather(error)
            else:
                errors = [error, ]
            for error in errors:
                if error is not None:
                    # handle the error on all ranks
                    msg = f"{rank}: caught error before collective comm!"
                    raise RuntimeError(msg) from error

            # gather values
            if comm is not None:
                values = comm.gather(new_value, root=0)
            else:
                values = [new_value, ]

            # print combined result
            if rank == 0:
                print(f"{rank}: {values}")

        except Exception as e:
                print(f"{rank}: skipping iteration {i}: {type(e)} {e}")
                continue


if __name__ == "__main__":
    main()
