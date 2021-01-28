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
        error = None
        if self.comm.rank == SyncIOComm.READ_RANK:
            try:
                data = func()
            except Exception as e:
                error = e

        # check for error
        error = self.comm.bcast(error, root=SyncIOComm.READ_RANK)
        if error is not None:
            # handle the error on all ranks
            msg = f"{self.comm.rank}: caught during read!"
            raise RuntimeError(msg) from error

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
        error = None
        if self.comm.rank == AsyncIOComm.READ_RANK:
            try:
                data = func()
            except Exception as e:
                error = e
            # self.comm.send(error, dest=AsyncIOComm.WORK_ROOT, tag=0)

        # check for error
        error = self.comm.bcast(error, root=AsyncIOComm.READ_RANK)
        if error is not None:
            # handle the error on all ranks
            msg = f"{self.comm.rank}: caught during read!"
            raise RuntimeError(msg) from error

        if self.comm.rank == AsyncIOComm.READ_RANK:
            self.comm.send(data, dest=AsyncIOComm.WORK_ROOT, tag=1)
        elif self.comm.rank == AsyncIOComm.WORK_ROOT:
            data = self.comm.recv(source=AsyncIOComm.READ_RANK, tag=1)
        else:
            pass

        return data

    def write(self, func, data):
        """WORK_ROOT sends `data` to WRITE_RANK. WRITE_RANK calls `func` to
        write `data`. This is a no-op for all other ranks.

        Args:
            func (method): function that writes `data`.
            data: the data to be written by `func`.
        """

        if self.comm.rank == AsyncIOComm.WRITE_RANK:
            error = self.comm.recv(source=AsyncIOComm.WORK_ROOT, tag=0)
            if error is not None:
                raise error
        else:
            pass

        if self.comm.rank == AsyncIOComm.WORK_ROOT:
            self.comm.send(data, dest=AsyncIOComm.WRITE_RANK, tag=2)
        elif self.comm.rank == AsyncIOComm.WRITE_RANK:
            data = self.comm.recv(source=AsyncIOComm.WORK_ROOT, tag=2)
            func(data)
        else:
            pass
