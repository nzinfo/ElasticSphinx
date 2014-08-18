# -*- coding: utf-8 -*-
"""
    处理数据库的同步信息
"""
import datetime
from .jsonfy import jsonify


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
        #print tbl_def, type(tbl_def)
        stmt = tbl_def.select()
        conn = self._engine.connect()
        try:
            rs = conn.execute(stmt)
            for row in rs:
                print jsonify(row)
        finally:
            conn.close()

#end of file
