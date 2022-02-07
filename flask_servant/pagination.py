import uuid
from marshmallow import Schema, fields as maFields
from datetime import timedelta, datetime


class PaginationCache(object):
    def __init__(self):
        self.cache = {}

class Paginator(object):
    def __init__(self, pagination=None, query_life=timedelta(minutes=10)):
        self.id = str(uuid.uuid4())
        self._query_life = query_life or timedelta(minutes=30)
        self.expires = datetime.utcnow() + self._query_life
        self.pagination = pagination

    @property
    def items(self):
        return self.pagination.items or []

    def refresh(self):
        self.expires = datetime.utcnow() + self._query_life

    def setPage(self, page=1):
        if page > self.pagination.pages:
            page = self.pagination.pages
        elif page < 1:
            page = 1

        if page == self.pagination.page:
            return

        if page > self.pagination.page:
            while page > self.pagination.page:
                self.pagination = self.pagination.next()
        elif page < self.pagination.page:
            while page < self.pagination.page:
                self.pagination = self.pagination.prev()


    def __repr__(self):
        return '<{}: "{}">'.format(self.__class__.__name__, self.id)

    def __str__(self):
        return self.id

    def __iter__(self):
        for i in self.pagination.items:
            yield i