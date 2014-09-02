# -*- coding: utf-8 -*-
"""
    处理数据库的同步信息
"""
import urllib
from .jsonfy import jsonify
from sqlalchemy.sql import column, select, alias, join, and_
from sqlalchemy import func


class DBSync(object):
    """
        同步数据库到 服务器 （Ledis）
        - 目前处理为输出 记录到 JSON 文件
        - 后续处理为特殊的指令
            PUT type values
    """
    def __init__(self, engine):
        self._engine = engine

    def sync_table(self, tbl_name, tbl_def):
        pg_size = 1000

        if tbl_name != 'Auction':
            return

        pk_names = [key.name for key in tbl_def.primary_key]
        pk_cols = [tbl_def.c[key.name] for key in tbl_def.primary_key]
        #print tbl_name, pk_names
        if len(pk_names) == 0:
            #print ("Plz assign primary key in %s." % tbl_name)
            return

        """
            SELECT * FROM `content` AS t1
    JOIN (SELECT id FROM `content` ORDER BY id desc LIMIT ".($page-1)*$pagesize.", 1) AS t2
    WHERE t1.id <= t2.id ORDER BY t1.id desc LIMIT $pagesize;
        """
        # check rec's count.
        cnt_items = dict()

        conn = self._engine.connect()
        # get all count.
        total_count = self._engine.execute(select([func.count()]).select_from(tbl_def)).scalar()

        #print total_count    # the total count of the table.
        def build_uri(names_, row_):
            items = {}
            for pk_name in names_:
                items[pk_name] = (row_[pk_name]).encode('utf8')
            return urllib.urlencode(items)

        def get_range_data(offset_, size_):
            tbl_main = alias(tbl_def, 't')
            join_condition = []

            pk_names_desc = [name+" DESC" for name in pk_names]
            sub_q = select(pk_cols).order_by(", ".join(pk_names_desc)).offset(offset_).limit(1).alias()

            for pk_name in pk_names:
                item = (tbl_main.c[pk_name] <= sub_q.c[pk_name])
                join_condition.append(item)

            if len(join_condition) > 1:
                j = join(tbl_main, sub_q, and_(*join_condition))
            else:
                j = join(tbl_main, sub_q, join_condition[0])

            return select([tbl_main]).select_from(j).order_by(", ".join(pk_names_desc)).limit(size_)

        try:
            for offset in range(0, total_count, pg_size):
                stmt = get_range_data(offset, pg_size)
                rs = conn.execute(stmt)
                for row in rs:
                    #print jsonify(row)
                    if row['ArtCode'] == 'art0000014880':
                        #print row, row['Click']
                        print jsonify(row)
                    #print row['WorkName'], type(row['WorkName'])
                    #cnt_items[build_uri(pk_names, row)] = 1
        finally:
            conn.close()

        if False:       # keep the code for [range select vs total select] data verify
            conn = self._engine.connect()
            try:
                stmt = select([tbl_def])
                rs = conn.execute(stmt)
                for row in rs:
                    cnt_items[build_uri(pk_names, row)] += 1
            finally:
                conn.close()
            # check
            for k in cnt_items:
                if cnt_items[k] != 2:
                    print k, '---------------'

#end of file
