import uuid
from marshmallow import Schema, fields as maFields
from datetime import timedelta, datetime
from sqlalchemy.orm import Query
from typing import Dict
import math


class Paginator(object):
    def __init__(self, query: Query, limit: int, query_life=timedelta(minutes=10)):
        self.id = str(uuid.uuid4())
        self.query = query
        self.total = query.count()
        self.limit = limit
        self.currentPage = 1
        self.pages = math.ceil(self.total / limit)
        self._query_life = query_life or timedelta(minutes=10)
        self.expires = datetime.utcnow() + self._query_life
        # self.results

    @property
    def results(self):
        return self.getResults(self.currentPage)

    @property
    def count(self):
        return len(self.getPage())

    def refresh(self):
        self.expires = datetime.utcnow() + self._query_life

    def next(self):
        if self.currentPage < self.pages:
            return self.getPage(self.currentPage + 1)
        return self.getPage(self.pages)

    def previous(self):
        if self.currentPage > 1:
            return self.getPage(self.currentPage - 1)
        return self.getPage(1)


    def getResults(self, offset: int=None):
        res = self.query.limit(self.limit)
        if offset:
            res = res.offset(offset)
        return res

    def getOffset(self, page) -> int:
        if page == 1 or page > self.pages:
            return 0
        return self.limit * (page-1)

    def getPage(self, page: int=None):
        if not page:
            page = self.currentPage
        if page != self.currentPage:
            self.currentPage = page
        return self.getResults(self.getOffset(page))

    def iterPages(self):
        for i in range(self.pages):
            yield self.getResults(self.getOffset(i+1))

    def getAllResults(self):
        return self.query.all()

    def __repr__(self):
        return '<{}: "{}">'.format(self.__class__.__name__, self.id)

    def __str__(self):
        return self.id

    def __iter__(self):
        for i in self.pagination.items:
            yield i


class PaginationCache(object):
    def __init__(self):
        self.cache: Dict[str, Paginator] = {}

    def flush(self):
        now = datetime.utcnow()
        for k in list(self.cache.keys()):
            if self.cache[k].expires < now:
                del self.cache[k]
    
    def get(self, uid: str) -> Paginator:
        pag = self.cache.get(uid)
        self.flush()
        return pag

    def add(self, paginator: Paginator) -> str:
        self.cache[paginator.id] = paginator
        self.flush()
        return paginator.id


PAGINATION_CACHE = PaginationCache()