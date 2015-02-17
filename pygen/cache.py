import md5, pickle, time

class SqlBackend:
    """A sqlite3/pysqlite2 database backend for the cache.
    Attempts to use sqlite3 first, and if that fails, tries
    pysqlite2."""
    currentVersion = 15
    def __init__(self, filename):
        try:
            import sqlite3
        except ImportError:
            from pysqlite2 import dbapi2 as sqlite3
        self.db = sqlite3.connect(filename)
        self.db.text_factory = str
        version = self.db.execute("PRAGMA user_version").fetchall()[0][0]
        if version > self.currentVersion:
            raise Exception, "Cache database newer than expected (expected %d, found %d)" % (self.currentVersion, version)
        if version != self.currentVersion:
            self.db.execute("DROP TABLE IF EXISTS cache")
            self.db.execute("""CREATE TABLE cache(
                md5 TEXT(32) NOT NULL PRIMARY KEY,
                lastAccessedDay INT NOT NULL,
                data TEXT NOT NULL)""")
            self.db.execute("PRAGMA user_version=%d" % self.currentVersion)

    def NowDayNumber(self):
        return int(time.time() / (24.0*60.0*60.0))

    def ExpireOldCacheEntries(self, days):
        """Expire any cache entry that hasn't been accessed in the last 'days' days."""
        expireTime = self.NowDayNumber() - days
        self.db.execute("DELETE FROM cache WHERE lastAccessedDay <= ?", [expireTime])
        self.db.commit()
            
    def DumpDB(self):
        """Debugging function, dump the whole cache to the screen."""
        cursor = self.db.cursor()
        items = cursor.execute("SELECT * FROM cache")
        print items.fetchall()
        cursor.close()

    def Read(self, md5):
        cursor = self.db.cursor()
        cursor.execute("SELECT data, lastAccessedDay FROM cache WHERE cache.md5=?", [md5])
        items = cursor.fetchall()
        if len(items) == 0:
            cursor.close()
            return None
        data, day = items[0]
        if day != self.NowDayNumber():
            cursor.execute("UPDATE cache SET lastAccessedDay=? WHERE cache.md5=?", [self.NowDayNumber(), md5])
        cursor.close()
        return data
    
    def Write(self, md5, data):
        self.db.execute("""INSERT OR REPLACE 
            INTO cache (md5, lastAccessedDay, data)
            VALUES(?, ?, ?)""", [md5, self.NowDayNumber(), data])
    
    def Flush(self):
        self.db.commit()
    
    def Close(self):
        self.db.commit()
        # Clear out old cache entries.
        self.ExpireOldCacheEntries(7)
        self.db.close()

class Cache:
    """A generic cache of objects, mapping one object to another.
    Uses an md5 hash of a pickle of the input object to determine
    identity."""
    def __init__(self, backend):
        self.backend = backend
        self.lastObject = None
        self.lastMD5 = None
    
    def __del__(self):
        self.Flush()
        self.backend.Close()
    
    def ObjectToMD5(self, object):
        if self.lastObject is object:
            return self.lastMD5
        self.lastObject = object
        self.lastMD5 = md5.new(pickle.dumps(object)).hexdigest()
        return self.lastMD5
    
    def Find(self, object):
        """Find the object 'object' in the cache.  Returns None if
        not in the cache, else returns the stored object."""
        md5 = self.ObjectToMD5(object)
        result = self.backend.Read(md5)
        if result:
            result = pickle.loads(result)
        return result 
    
    def Add(self, indexObject, cacheObject):
        """Adds an object 'cacheObject' into the cache, stored under
        'indexObject'."""
        md5 = self.ObjectToMD5(indexObject)
        data = pickle.dumps(cacheObject)
        self.backend.Write(md5, data)
        
    def Flush(self):
        """Flush the cache to disk, assuming it needs it.  Automatically called on destruction."""
        self.backend.Flush()

    
if __name__ == "__main__":
    cache = Cache(SqlBackend('temptest.db'))
    print cache.Find("monkey")
    cache.Add("monkey", "spaz")
    print cache.Find("monkey")
    cache.Add("monkey", (1,2,3,4))
    print cache.Find("monkey")
