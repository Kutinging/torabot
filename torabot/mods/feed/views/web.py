from flask import render_template
from ..query import parse as parse_query


def format_query_result(query):
    return {
        'uri': format_uri_result,
    }[parse_query(query.text).method](query)


def format_uri_result(query):
    return render_template('feed/result/uri.html', query=query)


def format_notice_body(notice):
    return {
        'feed.new': format_uri_notice
    }[notice.change.kind](notice)


def format_uri_notice(notice):
    return render_template('feed/notice/uri.html', notice=notice)


def format_help_page():
    return render_template('feed/help.html')
