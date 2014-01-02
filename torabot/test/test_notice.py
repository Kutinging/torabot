from .mixin import ModelMixin
from ..model import Session, User, Query
from .mock import mockrequests
from httmock import HTTMock
from ..sync import sync
from ..notice import pop_change
from .. import what
from ..sub import sub
from nose.tools import assert_equal, assert_is_none


class TestNotice(ModelMixin):

    def sync(self, session):
        with HTTMock(mockrequests):
            sync('大嘘', session)
        session.commit()

    def test_pop_change(self):
        s = Session()
        self.sync(s)
        new_count = 0
        reserve_count = 0
        for i in range(10):
            change = pop_change(s)
            assert change is not None
            if change.what == what.NEW:
                new_count += 1
            elif change.what == what.RESERVE:
                reserve_count += 1
            else:
                assert False
        assert_is_none(pop_change(s))
        assert_equal(new_count, 8)
        assert_equal(reserve_count, 2)

    def prepare(self, s):
        self.user = User(name='foo', email='bar', openid='http://foobar.com')
        s.add(self.user)
        s.flush()
        s.expire(self.user, ['id'])
        s.add(Query(text='大嘘'))
        s.commit()
        sub(user_id=self.user.id, query_text='大嘘', session=s)
        s.commit()

    def test_notice(self):
        s = Session()
        self.prepare(s)
        self.sync(s)
        for i in range(10):
            pop_change(s)
        assert_equal(len(self.user.notices), 10)
