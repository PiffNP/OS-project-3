import threading


class Database(object):
    def __init__(self):
        self.data = dict()
        self.locks = dict()

    def insert(self, key, value):
        print("insert")
        if key in self.data:
            return False
        self.data[key] = value
        return True

    def delete(self, key):
        print("delete")
        if key not in self.data:
            return None
        return self.data.pop(key)


    def get(self, key):
        print("get")
        if key not in self.data:
            return None
        return self.data.get(key)

    def update(self, key, value):
        print("update")
        if key not in self.data:
            return False
        self.data[key] = value
        return True
