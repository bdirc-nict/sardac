# coding: utf-8
import psycopg2

__constr = ""


def get_connection(con_str=None):
    if con_str is None:
        con_str = __constr
    return psycopg2.connect(con_str)


def connection_commit(connection):
    connection.commit()
