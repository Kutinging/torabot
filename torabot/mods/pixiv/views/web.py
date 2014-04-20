from flask import render_template
from logbook import Logger
from .. import name
from ..query import parse as parse_query
from ..translate import translate_mode


log = Logger(__name__)


def format_query_result(query):
    return {
        'user_id': format_user_result,
        'user_uri': format_user_result,
        'user_illustrations_uri': format_user_result,
        'ranking': format_ranking_result,
    }[parse_query(query.text).method](query)


def format_user_result(query):
    return render_template('pixiv/list.html', query=query)


def format_ranking_result(query):
    return render_template('pixiv/result/ranking.html', query=query)


def format_user_notice(notice):
    return "pixiv: <a href='%s'>%s</a> 更新了" % (
        notice.change.art.uri,
        notice.change.art.title,
    )


def format_ranking_notice(notice):
    return "pixiv: <a href='%(uri)s'>%(mode)s</a> 更新了" % dict(
        uri='http://www.pixiv.net/ranking.php?mode=%s' % notice.change.mode,
        mode=translate_mode(notice.change.mode)
    )


def format_notice_body(notice):
    return {
        'new': format_user_notice,
        'user_art.new': format_user_notice,
        'ranking': format_ranking_notice,
    }[notice.change.kind](notice)


def format_user_id_search():
    return render_template('pixiv/search/user_id.html', kind=name)


def format_user_uri_search():
    return render_template('pixiv/search/user_uri.html', kind=name)


def format_ranking_search():
    return render_template('pixiv/search/ranking.html', kind=name)


def format_advanced_search(**kargs):
    return {
        'user_id': format_user_id_search,
        'user_uri': format_user_uri_search,
        'ranking': format_ranking_search,
    }[kargs.get('method', 'user_uri')]()


def format_help_page():
    return render_template('pixiv/help.html')
