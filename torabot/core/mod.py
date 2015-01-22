import os
import json
import pkgutil
import importlib
from functools import partial
from asyncio import coroutine
from logbook import Logger
from datetime import datetime, timedelta
from nose.tools import assert_is_instance
from flask import current_app
import abc
from ..ut.facade import Facade
from ..db import db
from . import core


log = Logger(__name__)


@core.initializer
def init_app(app):
    app.config.setdefault('TORABOT_QUERY_EXPIRE', 15 * 60)
    app.config.setdefault('TORABOT_SYNC_ON_EXPIRE', True)


class InstanceField(object):

    def __get__(self, obj, cls):
        if cls is None:
            cls = type(obj)
        return core.mod(cls.name)


@core.setattr
class Mod(Facade, metaclass=abc.ABCMeta):

    instance = InstanceField()

    @abc.abstractproperty
    def name(self):
        pass

    @abc.abstractproperty
    def display_name(self):
        pass

    @abc.abstractproperty
    def has_advanced_search(self):
        pass

    @abc.abstractproperty
    def has_normal_search(self):
        pass

    @abc.abstractproperty
    def no_empty_query(self):
        pass

    @abc.abstractproperty
    def description(self):
        pass

    @property
    def state_id(self):
        return 'mod_' + self.name

    def guess_name(self, query):
        return query.text

    @abc.abstractmethod
    def changes(self, old, new):
        pass

    @abc.abstractmethod
    def source(self, query):
        pass

    @abc.abstractmethod
    def regular(self, query):
        '''return most standard query kind and text'''
        pass

    @db.with_optional_bind
    @coroutine
    def search(self, text, *, bind, sync_on_expire=None):
        '''return None means first sync failed'''

        if self.no_empty_query and not text:
            raise core.CoreError("Mod %s don't accept empty query" % self.name)

        @coroutine
        def get_query():
            with db.connection_context(bind=bind) as conn:
                return (yield from db.get_query_bi_kind_and_text(conn, self.name, text))

        @coroutine
        def sync():
            return (yield from core.sync(kind=self.name, text=text, bind=bind))

        @coroutine
        def has():
            with db.connection_context(bind=bind) as conn:
                query = yield from db.get_query_bi_kind_and_text(conn, self.name, text)
                return bool(query and query.result)

        if not (yield from has()):
            log.info('query {} of {} dosn\'t exist', text, self.name)
            if (yield from sync()):
                query = yield from get_query()
            else:
                query = None
        else:
            query = yield from get_query()
            if (yield from self.expired(query)):
                log.debug('query {} of {} expired', text, self.name)
                if (
                    (yield from self.sync_on_expire(query))
                    if sync_on_expire is None
                    else sync_on_expire
                ):
                    if (yield from sync()):
                        query = yield from get_query()
                    else:
                        log.debug(
                            'sync {} of {} timeout or meet expected error',
                            text,
                            self.name
                        )
                else:
                    log.debug('mark query {} of {} need sync', text, self.name)
                    with db.connection_context(commit=True, bind=bind) as conn:
                        yield from db.set_next_sync_time_bi_kind_and_text(
                            conn,
                            self.name,
                            text,
                            datetime.utcnow()
                        )

        if query is not None and not query.result:
            raise core.CoreError('Invalid query: {}'.format(query))

        return query

    @coroutine
    def expired(self, query):
        return query.mtime + timedelta(seconds=self.life(query)) < datetime.utcnow()

    def life(self, query):
        t = current_app.config['TORABOT_QUERY_EXPIRE']
        assert_is_instance(t, int)
        return t

    @coroutine
    def sync_on_expire(self, query):
        return current_app.config['TORABOT_SYNC_ON_EXPIRE']

    @abc.abstractmethod
    def format_notice_status(self, view, notice):
        pass

    @abc.abstractmethod
    def format_notice_body(self, view, notice):
        pass

    def format_query_text(self, view, text):
        return text

    @abc.abstractmethod
    def format_query_result(self, view, query):
        pass

    @abc.abstractmethod
    def format_advanced_search(self, view, **kargs):
        pass

    def format_help_page(self):
        return ''

    def notice_attachments(self, view, notice):
        return []


class ViewMixin(object):

    @property
    def views(self):
        return self.get_views(current_app)

    def get_views(self, app):
        value = self.get_state(app).get('views')
        if value is None:
            self.get_state(app)['views'] = value = {}
            root = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                '..',
                'mods',
                self.name,
                'views'
            ))
            try:
                for _, name, _ in pkgutil.iter_modules([root]):
                    value[name] = importlib.import_module(
                        '...mods.%s.views.%s' % (self.name, name),
                        __name__
                    )
            except:
                log.info('Load views package of {} failed', self.name)
        return value

    def format_notice_status(self, view, notice):
        func = getattr(self, '%s_format_notice_status' % view, None)
        if func is None:
            func = self.views[view].format_notice_status
        return func(notice)

    def format_notice_body(self, view, notice):
        func = getattr(self, '%s_format_notice_body' % view, None)
        if func is None:
            func = self.views[view].format_notice_body
        return func(notice)

    def format_query_text(self, view, text):
        func = getattr(self, '%s_format_query_text' % view, None)
        if func is None:
            func = getattr(self.views[view], 'format_query_text', None)
        if func is None:
            func = partial(super().format_query_text, view)
        return func(text)

    def format_query_result(self, view, query):
        func = getattr(self, '%s_format_query_result' % view, None)
        if func is None:
            func = self.views[view].format_query_result
        return func(query)

    def format_advanced_search(self, view, **kargs):
        func = getattr(self, '%s_format_advanced_search' % view, None)
        if func is None:
            func = self.views[view].format_advanced_search,
        return func(**kargs)

    def format_help_page(self, view):
        func = getattr(self, '%s_format_help_page' % view, None)
        if func is None:
            func = self.views[view].format_help_page
        return func(view)

    def notice_attachments(self, view, notice):
        func = getattr(self, '%s_notice_attachments' % view, None)
        if func is None:
            func = getattr(self.views[view], 'notice_attachments', None)
        if func is None:
            func = partial(super().notice_attachments, view)
        return func(notice)


def field_guess_name_mixin(field, *args):
    if isinstance(field, str):
        fields = [field]
    else:
        fields = field
    fields.extend(args)

    class FieldGuessNameMixin(object):

        def guess_name(self, query):
            try:
                d = json.loads(query.text)
                if isinstance(d, dict):
                    for name in fields:
                        value = d.get(name, None)
                        if value:
                            return value
            except:
                pass
            return super(FieldGuessNameMixin, self).guess_name(query)

    return FieldGuessNameMixin


class GuessNameFromQueryText(object):

    def guess_name(self, query):
        return query.text


__all__ = ['Mod', 'ViewMixin']
