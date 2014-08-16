# -*- coding: utf-8 -*-
"""
    根据 JSON 的定义， 重新生成 ORM 的代码。
"""
import os
import json
from jinja2 import Environment, DictLoader

from .db_conn import cs_create_engine
import sqlalchemy
from sqlalchemy import inspect


SQLALCHEMY_SCHEMA_TEMPLATE = \
"""
import sqlalchemy
from sqlalchemy import create_engine,text
from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy import BIGINT, BINARY, BLOB, BOOLEAN, CHAR, CLOB, \\
    DATE, DATETIME, DECIMAL, FLOAT, INTEGER, NCHAR, \\
    NVARCHAR, NUMERIC, REAL, SMALLINT, TEXT, TIME, TIMESTAMP, VARBINARY, VARCHAR
{% if dialect=='mysql' %}from sqlalchemy.dialects.mysql import \\
    VARCHAR
{% else %}from sqlalchemy.dialects.postgresql import \\
    ARRAY, BIGINT, BIT, BOOLEAN, BYTEA, CHAR, CIDR, DATE, \\
    DOUBLE_PRECISION, ENUM, FLOAT, INET, INTEGER, INTERVAL, \\
    MACADDR, NUMERIC, REAL, SMALLINT, TEXT, TIME, TIMESTAMP, \\
    UUID, VARCHAR, JSON, INET
{% endif %}

class SQLDBSchema(object):
    name = "schema"

    def __init__(self, meta):
        metadata = self._meta = meta
        {% for tbl_name, tbl in tables.items() %}
        self._tables["{{ tbl['name'] }}"] = \\
            Table("{{ tbl['name'] }}", metadata, {% for col in tbl['columns'] %}
                 Column("{{ col['name'] }}", {{ col | col_sql_type }}, nullable={{ col['nullable'] }}, {{ col | col_sql_default }} ), {% endfor %}
                 {% if tbl['primary']['constrained_columns'] %}
                 PrimaryKeyConstraint({{ tbl | tbl_pk}}), {% endif %}
                 {% for idx in tbl['index'] %}
                 Index({{ idx| idx_sql_def }}), {% endfor %}
                 )
        {% endfor %}
"""


def col_sql_type(col):
    if col['type'] in ['CHAR', 'NCHAR', 'NVARCHAR', 'VARBINARY', 'VARCHAR']:        # VARBINARY might have no len.
        #print col['type'], col
        return "%s(%d)" % (col['type'], col['length'])
    return col['type']


def col_sql_default(col):
    if 'default' in col:
        if col['default'][0] == "'":
            return 'server_default=text(%s), ' % col['default']
        else:
            return "server_default=text('%s'), " % col['default']
    return ""


def tbl_pk(tbl):
    primary = tbl['primary']
    cols = primary['constrained_columns']
    cols = ['"%s"' % x for x in cols]
    pks = ', '.join(cols)
    if 'name' in primary and primary['name']:
        return pks+(", name='%s'" % primary['name'])
    else:
        return pks


def idx_sql_def(idx):
    # FIXME: 此处没有处理索引本身的类型。在PG中，是支持多种索引类型的。
    # 'idx_col34', 'col3', 'col4', unique=True
    cols = idx['column_names']
    cols = ['"%s"' % x for x in cols]
    cols_str = ', '.join(cols)
    if idx['unique']:
        return '"%s", %s, unique=True' % (idx['name'], cols_str)
    else:
        return '"%s", %s' % (idx['name'], cols_str)


class DBSchemaCodeGen(object):
    """
        用于代码生成
    """
    def __init__(self, engine):
        self._engine = engine
        self._table_names = []

    def generate(self, json_table_def_path, dialect='mysql', orm='sqlalchemy'):
        #print json_table_def_path
        #global TABLE_WWWSQL_XML_TEMPLATE
        env = Environment(loader=DictLoader({}))
        env.filters['col_sql_type'] = col_sql_type
        env.filters['col_sql_default'] = col_sql_default
        env.filters['tbl_pk'] = tbl_pk
        env.filters['idx_sql_def'] = idx_sql_def


        if orm == 'sqlalchemy':
            template = env.from_string(SQLALCHEMY_SCHEMA_TEMPLATE)

        if orm == 'pony':
            template = env.from_string(SQLALCHEMY_SCHEMA_TEMPLATE)

        # FIXME: 目前不支持 外键约束， 需要由其他机制定义（一个主要的原因是更多的关系是引用，而非严格的约束）
        # ForeignKeyConstraint(['other_id'], ['othertable.other_id']),

        tables = {}
        for fname  in os.listdir(json_table_def_path):
            tbl_name, ext = os.path.splitext(fname)
            if ext != ".json":
                continue
            # table name
            fname = os.path.join(json_table_def_path, fname)
            with open(fname, 'rb') as fh:
                meta_obj = json.load(fh)
            tables[tbl_name] = meta_obj
        # generate code via template

        #print __file__
        ctx = template.render(dialect=dialect, tables=tables)
        return ctx

# end of file.