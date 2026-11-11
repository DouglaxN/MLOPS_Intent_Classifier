import os
import copy
import pymongo

MONGO_URL = os.environ['MONGO_URL'] 
MONGO_DB = os.environ.get('MONGO_DB', 'intent_classifier')
MONGO_PRED_COLLECTION = os.environ.get('MONGO_PRED_COLLECTION', 'predictions')

client = pymongo.MongoClient(MONGO_URL, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000)

db = client[MONGO_DB]


class _ResilientCollection:
    def __init__(self, real_col):
        self._real = real_col
        self._mem = []

    def insert_one(self, doc):
        try:
            return self._real.insert_one(doc)
        except Exception:
            doc['_id'] = 'mem_id'
            self._mem.append(copy.deepcopy(doc))
            return None

    def find(self, filter_spec=None, projection=None):
        try:
            docs = list(self._real.find(filter_spec or {}, projection))
            return _ResilientCursor(docs)
        except Exception:
            docs = [
                {k: v for k, v in copy.deepcopy(d).items() if k != '_id'}
                for d in self._mem
            ]
            return _ResilientCursor(docs)


class _ResilientCursor:
    def __init__(self, docs):
        self._docs = docs

    def sort(self, key, direction=-1):
        parts = key.split('.')
        def _get(d):
            cur = d
            for p in parts:
                cur = cur.get(p, '') if isinstance(cur, dict) else ''
            return str(cur)
        self._docs.sort(key=_get, reverse=(direction == -1))
        return self

    def limit(self, n):
        self._docs = self._docs[:n]
        return self

    def __iter__(self):
        return iter(self._docs)


prediction_collection = _ResilientCollection(db[MONGO_PRED_COLLECTION])