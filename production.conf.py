# DEBUG or NOT
DEBUG = 1  #测试调试开关


DATABASE_DEFAULT_URL = 'mysql://root:root@127.0.0.1:8889/auction?charset=utf8'
DEFAULT_META_PATH = 'meta'
DEFAULT_APP_PATH = 'demoapp'

DATABASE_DEFAULT_SCHEMA_DEFINE = 'demoapp.schema.sql_schema.SQLDBSchema'

# 开发阶段使用的数据库，默认的对数据库的更新都在此
DATABASE_DEFAULT_DEV_URL = 'mysql://root:root@127.0.0.1:8889/auction_dev?charset=utf8'
# BDD阶段测试使用的数据库
DATABASE_DEFAULT_TEST_URL = 'mysql://root:root@127.0.0.1:8889/auction_test'

# Sphinx 有关的存储配置

"""
    数据库的访问方式
"""
DATABASES = dict()

DATABASES['auction'] = {
    'ObjectStore': {
        'type': 'redis',
        'url': 'redis://localhost:6379/1'
    },
    'DataBase': {
        'url': 'mysql://root:root@127.0.0.1:8889/auction_dev?charset=utf8'
    }
}

"""
    存储配置等 Meta 信息的方式
"""
DATABASE_META = {
    'type': 'redis',
    'url': 'redis://localhost:6379/0'
}