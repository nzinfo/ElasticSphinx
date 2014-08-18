# -*- coding: utf-8 -*-
"""
    用于处理 ObjSpace 的命令行接口
    1 import <连接名>
        将某数据库中对表的定义，导入系统。 可能会丢失信息，尽最大可能导入；
        保存为 JSON 格式

    2 generate <连接名>
        根据 JSON 的定义，生成有效的 PonyORM 的表结构定义
        根据 JSON 的定义，生成有效的 SQLAlchemy 的表结构定义
        - 是否支持 不同的表 生成 不同的文件？
        (基本假设：从遗留的系统启动，开始系统开发的流程)

    3 rebuild
        （PonyORM | SQLAlchemy 的均支持）
        根据数据库的定义(Python)， 更新 表的文件定义 (删除、重建)

    4 init
        根据预制 SQL 初始化数据

    5 sync
        同步数据库的数据到 `Redis` 中，实际为自己改写的；

    6 tigger

        在数据库中，创建同步数据需要的触发器 和 其他辅助结构
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


class DatabaseImport(Command):
    """
        Read DataSchema Define from Database [name], and write to Tables' YAML
    """
    option_list = (
        Option("-d", "--debug", dest='debug_flag', action="count", required=False, default=0,
               help='debug flag'),
        Option(metavar='dbname', dest='dbname', help='database to be import', nargs='+'),
    )

    def run(self, debug_flag, dbname):
        app = flask.current_app
        for db in dbname:
            conn_str = app.config['DATABASE_%s_URL' % db.upper()]
            meta_path = app.config['%s_META_PATH' % db.upper()]
            meta_path = os.path.abspath(meta_path)
            app.db_engine = space.cs_create_engine(app, conn_str)
            inspector = space.DBInspector(app.db_engine)
            # call inspector
            for tbl_name in inspector.tables():
                meta = inspector.table_define(tbl_name)
                meta_file = os.path.join(meta_path, "%s.json" % tbl_name)
                with open(meta_file, 'wb') as fh:
                    json.dump(meta.to_jsonable(), fh,  sort_keys=True,
                              indent=4, separators=(',', ': '))
            app.db_engine = None
        pass
        # end of file.


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
    mgr.add_command('import', DatabaseImport())
    mgr.add_command("rebuild", DatabaseRebuild())
    mgr.add_command("generate", DatabaseGenerate())
    mgr.add_command("sync", DatabaseSync())
    #manager.add_command("dict", dict_cli.getManager(app))
    return mgr

if __name__ == "__main__":
    manager = setup_manager(create_app)
    manager.add_option('-c', '--config', dest='config', required=False)
    manager.run()


# end of file
