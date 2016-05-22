import threading
import time
from threading import Lock
from read_write_lock import ReadWriteLock


class Database(object):
    def __init__(self):
        self.data = dict()
        self.locks = dict()  # locks on each data
        self.modify_lock = ReadWriteLock()  # lock on modification of data structure

    def insert(self, key, value):
        self.modify_lock.acquire_write()
        if key in self.data:
            self.modify_lock.release_write()
            return False
        self.locks[key] = ReadWriteLock()
        self.data[key] = value  # can safely be done because the acquire_write
        self.modify_lock.release_write()
        return True

    def delete(self, key):
        self.modify_lock.acquire_write()
        if key not in self.data:
            self.modify_lock.release_write()
            return None
        val = self.data.pop(key) # can safely be done because the acquire_write
        self.locks.pop(key)  # because acquire_write on modify_lock, no one holds this lock so no problem
        self.modify_lock.release_write()
        return val

    def get(self, key):
        self.modify_lock.acquire_read()
        dlock = self.locks.get(key, None)
        if dlock is None:
            self.modify_lock.release_read()
            return None
        dlock.acquire_read()
        val = self.data.get(key)
        dlock.release_read()
        self.modify_lock.release_read()  # don't want dlock to be deleted in case
        return val

    def update(self, key, value):
        self.modify_lock.acquire_read()
        dlock = self.locks.get(key, None)
        if dlock is None:
            self.modify_lock.release_read()
            return False
        dlock.acquire_write()
        self.data[key] = value
        dlock.release_write()
        self.modify_lock.release_read()  # don't want dlock to be deleted in case
        return True
