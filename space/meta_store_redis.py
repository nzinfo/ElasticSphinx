# -*- coding: utf-8 -*-
"""
    Meta 信息的访问接口
    - 配置了多少个数据库
    - 数据库中有多少个表
    - 具体表的字段定义
    - 修改表的字段定义
    - 定义表之间的关系


"""


class MetaStoreRedis(object):
    """
        存储数据库配置的元信息， 提供统一的访问接口
        在 Redis 协议上的实现，默认数据存在 db=0 中， 前缀 _$meta

    """

    def databases(self):
        """
        :return:    系统中，配置文件配置的全部数据库的名称
        """
        return []

    def tables(self, db_name):
        """
        数据库中，定义好的全部的表名称
        - 在 Redis 中，为一个 Set
        :param db_name:
        :return:
        """

    def table(self, db_name, tbl_name):
        """
            数据表的：
                - 字段定义
                - 主键
                - 表与表的关系
        :param db_name:
        :param tbl_name:
        :return:
        """

    def set_table(self, db_name, tbl_name, tbl_json_ctx):
        """
            更新表的 ctx 定义
            ？ 是否单独更新 表之间的关系？
        :param db_name:
        :param tbl_name:
        :param tbl_json_ctx:
        :return:
        """
        pass


# end of file