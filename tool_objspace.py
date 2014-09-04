# -*- coding: utf-8 -*-
"""
    用于处理 ObjSpace 的命令行接口
"""

import json
import os
import flask
from flask import Flask
from flask.ext.script import Manager, Command, Option

import space


def create_app(config=None):
    # configure your app
    app = Flask(__name__)
    if config is None:
        #print app.root_path
        config = os.path.join(app.root_path, 'production.conf.py')

    app.config.from_pyfile(config)
    app.config.DEBUG = app.config['DEBUG']
    return app


def script_path(file_macro):
    return os.path.abspath(os.path.dirname(file_macro))


class DatabaseSchema(Command):
    """
        读取对应的数据库配置，
        - 此处的数据库名称，为配置文件中的名称
    """
    option_list = (
        Option("-d", "--debug", dest='debug_flag', action="count", required=False, default=0,
               help='debug flag'),
        Option("-w", "--write", dest='write_flag', metavar='write schema', required=False, default=False,
               help='update table schema'),
        Option("-s", "--sync", dest='sync_flag', metavar='sync schema', required=False, default=False,
               help='sync table schema from database'),
        Option(metavar='dbname', dest='db_name', help='database to be import'),
        Option(metavar='tblname', dest='tbl_name', help='table name', nargs='?'),
    )

    def run(self, debug_flag, write_flag, sync_flag, db_name, tbl_name):
        """
            TODO:
            1 read & check db_name existed in app.config
            2 get meta connection config from app.config
            3 check action
                3.1 read info with tbl_name is None
                    -> list all tables in the db_name
                        - db_name 未同步过 （ 404 Not found)
                        - 数据正常

                3.2 read info with tbl_name
                    -> print json's fields & primary key  & table relation

                3.3 update table define.
                    -> read define from std
                        1 check schema , all column existed in database(sql)
                        2 check pk, is defined as pk (skip now)
                        3 check relation, refer table existed , refer column existed.

            Note: 不提供列出全部 配置过的数据库的命令，这个可以通过读配置文件很容易的发现
        """
        app = flask.current_app
        print db_name, tbl_name
        pass
        # end of file.


class DatabaseConfig(Command):
    """
        命令行形式的全局配置
        - mode 工作模式： 作为 meta & 作为 worker
        - meta Meta机器的地址
        - hostname 本机的名称
    """
    option_list = (
        Option("-d", "--debug", dest='debug_flag', action="count", required=False, default=0,
               help='debug flag'),
        Option("-w", "--write", dest='write_flag', metavar='write config', required=False, default=False,
               help='update config'),
        Option(metavar='cmd', dest='cmd', help='action, in [mode|meta|hostname] '),
        Option(metavar='value', dest='value', help='new value', nargs=1),
    )

    def run(self, debug_flag, write_flag, cmd, value):
        """
            TODO:
            1 read setting able config ( settings.py ) in current script 's path
            2 check cmd in ['mode', 'meta', 'hostname']
        """
        app = flask.current_app


class DatabaseChannel(Command):
    """
        索引频道的配置
        - schema [channel_name] @meta 索引的字段的配置 | 涉及哪些表 （JSON 形式） [读写]
        - join [channel_name] [port]  @worker 加入某个索引
        - leave [channel_name]  @worker 离开某个索引
        - worker [channel_name] 列出全部参与该 channel 的节点
        - list  列出全部的频道列表
    """
    option_list = (
        Option("-d", "--debug", dest='debug_flag', action="count", required=False, default=0,
               help='debug flag'),
        Option("-w", "--write", dest='write_flag', metavar='write config', required=False, default=False,
               help='update config'),
        Option(metavar='cmd', dest='cmd', help='action, in [mode|meta|hostname] '),
        Option(metavar='value', dest='value', help='new value', nargs='*'),
    )


class DatabaseControl(Command):
    """
        控制集群
        - start [channel_name] @meta @worker 启动某个 channel ，如果是在 worker 上执行，则只影响到本 worker 的
        - stop  ...
        - start | stop with worker
        - status 集群的状态 | channel 的状态，最后一次重建时间等
        - if not channel_name, deal with the whole cluster `only @meta`

    """
    option_list = (
        Option("-d", "--debug", dest='debug_flag', action="count", required=False, default=0,
               help='debug flag'),
        Option("-w", "--worker", dest='worker', metavar='write node', required=False, default=None,
               help='especial worker'),
        Option(metavar='cmd', dest='cmd', help='action, in [start|stop|restart|status]'),
        Option(metavar='channel', dest='channel', help='channel name', nargs='?'),
    )


class DatabaseSync(Command):
    """
        同步数据
        - [database] [table] 同步
        - --all [database] [table] 同步全部数据
        如果不给出具体的表名，则为全部表同步
    """
    option_list = (
        Option("-d", "--debug", dest='debug_flag', action="count", required=False, default=0,
               help='debug flag'),
        Option("--all", dest='flag_full_sync', metavar='full sync', required=False, default=False,
               help='do full sync'),
        Option(metavar='dbname', dest='db_name', help='database to be sync'),
        Option(metavar='tblname', dest='tbl_name', help='table name', nargs='?'),
    )


class DatabasePolicy(Command):
    """
        配置同步数据的策略
        - policy_log [database] [table] 创建同步需要的日志表需要的表结构与触发器
    """
    option_list = (
        Option("-d", "--debug", dest='debug_flag', action="count", required=False, default=0,
               help='debug flag'),
        Option(metavar='cmd', dest='cmd', help='action, in [policy_log]'),
        Option(metavar='dbname', dest='db_name', help='database to be sync'),
        Option(metavar='tblname', dest='tbl_name', help='table name', nargs='?'),
    )


class DatabaseIndex(Command):
    """
        创建索引
        - [channel_name]  @meta 全部重建
        - [channel_name]  @worker 只重建该worker上的
    """
    option_list = (
        Option("-d", "--debug", dest='debug_flag', action="count", required=False, default=0,
               help='debug flag'),
        Option(metavar='channel', dest='channel_name', help='index channel to be build.'),
        Option(metavar='tblname', dest='tbl_name', help='table name', nargs='?'),
    )

class DatabaseGenerate(Command):
    """
        Generate Python's ORM define.
        - PonyORM
        - SQLAlchemy
    """
    option_list = (
        Option("-d", "--debug", dest='debug_flag', action="count", required=False, default=0,
               help='debug flag'),
        Option(metavar='name', dest='db_names', help='generate python code for which database(s)', nargs='+'),
    )

    def run(self, debug_flag, db_names):
        app = flask.current_app
        for db in db_names:
            conn_str = app.config['DATABASE_%s_URL' % db.upper()]

            meta_path = app.config['%s_META_PATH' % db.upper()]
            meta_path = os.path.abspath(meta_path)

            app_path = app.config['%s_APP_PATH' % db.upper()]
            app_path = os.path.abspath(app_path)
            sqlalchemy_file = os.path.join(app_path, 'schema', 'sql_schema.py')
            app.db_engine = space.cs_create_engine(app, conn_str)
            gen = space.DBSchemaCodeGen(app.db_engine)
            if conn_str.find('mysql') == 0:
                code = gen.generate(meta_path, 'mysql', 'sqlalchemy')
                with open(sqlalchemy_file, 'wb') as fh:
                    fh.write(code)
                code = gen.generate(meta_path, 'mysql', 'pony')
            else:
                code = gen.generate(meta_path, 'postgresql', 'sqlalchemy')
            # write to file
            #print code
            pass


class DatabaseRebuild(Command):
    """
        Rebuild table & index
    """
    option_list = (
        Option("-d", "--debug", dest='debug_flag', action="count", required=False, default=0,
               help='debug flag'),
        Option(metavar='schema', dest='db_schema', help='which schema create table in.'),
        Option(metavar='name', dest='db_names', help='generate python code for which database(s)', nargs='+'),
    )

    def run(self, debug_flag, db_schema, db_names):
        app = flask.current_app
        for db in db_names:
            conn_str = app.config['DATABASE_%s_DEV_URL' % db.upper()]
            schema_cls_name = app.config['DATABASE_%s_SCHEMA_DEFINE' % db.upper()]
            #print schema_cls_name
            meta_path = app.config['%s_META_PATH' % db.upper()]
            meta_path = os.path.abspath(meta_path)
            app.db_engine = space.cs_create_engine(app, conn_str)
            # set schema.
            obj = space.load_class(schema_cls_name)
            if obj is None:
                print 'can not found %s.' % schema_cls_name
                return

            obj = obj()         # create the schema object.
            for tbl in obj._tables:
                #obj._tables[tbl].schema = db_schema
                obj._tables[tbl].drop(app.db_engine, checkfirst=True)
                obj._tables[tbl].create(app.db_engine, checkfirst=True)
            pass


class DatabaseSync(Command):
    """
        Sync Data from SQLDatabase -> ObjStore(LedisDB)
    """
    option_list = (
        Option("-d", "--debug", dest='debug_flag', action="count", required=False, default=0,
               help='debug flag'),
        Option(metavar='schema', dest='db_schema', help='which schema create table in.'),
        Option(metavar='name', dest='db_names', help='generate python code for which database(s)', nargs='+'),
    )

    def run(self, debug_flag, db_schema, db_names):
        app = flask.current_app
        for db in db_names:
            conn_str = app.config['DATABASE_%s_DEV_URL' % db.upper()]
            schema_cls_name = app.config['DATABASE_%s_SCHEMA_DEFINE' % db.upper()]
            #print schema_cls_name
            meta_path = app.config['%s_META_PATH' % db.upper()]
            meta_path = os.path.abspath(meta_path)
            app.db_engine = space.cs_create_engine(app, conn_str, True)
            # set schema.
            obj = space.load_class(schema_cls_name)
            if obj is None:
                print 'can not found %s.' % schema_cls_name
                return

            db_syncer = space.DBSync(app.db_engine)

            obj = obj()         # create the schema object.
            for tbl in obj._tables:
                db_syncer.sync_table(tbl, obj._tables[tbl])
                #print tbl


def setup_manager(app):
    mgr = Manager(app)
    mgr.add_command('schema', DatabaseSchema())
    mgr.add_command("config", DatabaseConfig())
    mgr.add_command("channel", DatabaseChannel())
    mgr.add_command("ctrl", DatabaseControl())
    mgr.add_command("sync", DatabaseSync())
    mgr.add_command("index", DatabaseIndex())
    # TODO: runserver 有 两个模式  @meta @worker
    return mgr

if __name__ == "__main__":
    manager = setup_manager(create_app)
    manager.add_option('-c', '--config', dest='config', required=False)
    manager.run()


# end of file
