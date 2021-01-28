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
        total = sum(subtotals)
        print(self.msg(f"total = {total}"))

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
        return self.comm.rank >= AsyncIOComm.WORK_ROOT

    def is_worker_root(self):
        return self.comm.rank == AsyncIOComm.WORK_ROOT

    def read(self, func, data):
        if self.comm.rank == AsyncIOComm.READ_RANK:
            data = func()
            self.comm.send(data, dest=AsyncIOComm.WORK_ROOT, tag=1)
        elif self.comm.rank == AsyncIOComm.WORK_ROOT:
            data = self.comm.recv(source=AsyncIOComm.READ_RANK, tag=1)
        return data

    def write(self, func, data):
        if self.comm.rank == AsyncIOComm.WORK_ROOT:
            self.comm.send(data, dest=AsyncIOComm.WRITE_RANK, tag=2)
        elif self.comm.rank == AsyncIOComm.WRITE_RANK:
            data = self.comm.recv(source=AsyncIOComm.WORK_ROOT, tag=2)
            func(data)