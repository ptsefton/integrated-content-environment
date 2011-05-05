


class _Status(object):
    __slots__ = ["__value"]
    
    @property
    def added(self):
        return "added"
    
    @property
    def modified(self):
        return "modified"
    
    @property
    def deleted(self):
        return "deleted"
    
    @property
    def recreated(self):
        return "recreated"
    
    @property
    def missing(self):
        return "missing"
    
    def __str__(self):
        return self.__value


Status = _Status()


class Schedule(object):
    __slots__ = []
    # Added, Deleted, Modified
    
    def __init__(self):
        pass
    


