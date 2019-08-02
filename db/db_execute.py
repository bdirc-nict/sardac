# coding: utf-8
from .db_connect import get_connection


def create_sql(table_name, values):
    # TODO

    tuplist = [(k, values[k]) for k in values]

    sql = "INSERT INTO {0}".format(table_name)
    sql += "({0}) VALUES ({1})".format(",".join(tup[0] for tup in tuplist), ",".join(create_value_exp(tup[1]) for tup in tuplist))

    return sql


def insert_with_commit(connection, table_name, specific_values):
    if connection is None:
        with get_connection() as conn:  # TODO
            insert_with_commit(conn, table_name, specific_values)
    else:
        with connection.cursor() as cur:
            sql = create_sql(table_name, specific_values)
            cur.execute(sql)
            print(sql)
            connection.commit()


def insert(connection, table_name, specific_values):
    if connection is None:
        with get_connection() as conn:  # TODO
            insert_with_commit(conn, table_name, specific_values)
    else:
        with connection.cursor() as cur:
            sql = create_sql(table_name, specific_values)
            cur.execute(sql)
            print(sql)


def execute_with_commit(connection, sql):
    if connection is None:
        with get_connection() as conn:  # TODO
            execute_with_commit(conn, sql)
    else:
        with connection.cursor() as cur:
            cur.execute(sql)
            connection.commit()


def execute(connection, sql):
    if connection is None:
        with get_connection() as conn:  # TODO
            insert_with_commit(conn, sql)
    else:
        with connection.cursor() as cur:
            cur.execute(sql)


def create_value_exp(value):
    if value is None:
        return "NULL"
    if type(value) is tuple and value[0] == "raw":
        return value[1]
    return "'{0}'".format(value)
