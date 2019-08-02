# coding: utf-8
from .db_connect import get_connection


def select_one_record(connection, sql):
    if connection is None:
        with get_connection() as conn:  # TODO
            select_one_record(conn, sql)
    else:
        with connection.cursor() as cur:
            cur.execute(sql)
            row = cur.fetchone()
            return row
