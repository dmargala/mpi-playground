class NoMPIComm(object):
    def __init__(self):
        self.comm = None
        self.rank = 0
        self.size = 1

    def bcast(self, rootfunc, root=0):
        return rootfunc()

    def gather(self, rankfunc, root=0):
        return [rankfunc(), ]


class SafeMPIComm(object):
    def __init__(self, comm):
        self.comm = comm
        self.rank = comm.rank
        self.size = comm.size

    def bcast(self, rootfunc, root=0):
        # only root rank calls rootfunc
        obj = None
        error = None
        try:
            if self.rank == root:
                obj = rootfunc()
        except Exception as e:
            # only root catches error here
            error = e

        # check for error
        error = self.comm.bcast(error, root=root)
        if error is not None:
            # handle the error on all ranks
            msg = f"{self.rank}: caught error before collective comm!"
            raise RuntimeError(msg) from error

        return self.comm.bcast(obj, root=root)

    def gather(self, rankfunc, root=0):
        # all ranks call rankfunc
        error = None
        try:
            sendobj = rankfunc()
        except Exception as e:
            # only ranks with an error catch here
            error = e

        # check for error
        errors = self.comm.allgather(error)
        for error in errors:
            if error is not None:
                # handle the error on all ranks
                msg = f"{self.rank}: caught error before collective comm!"
                raise RuntimeError(msg) from error

        return self.comm.gather(sendobj, root=root)
