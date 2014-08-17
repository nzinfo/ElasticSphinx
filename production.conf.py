# DEBUG or NOT
DEBUG = 1  #测试调试开关


DATABASE_DEFAULT_URL = 'mysql://root:root@127.0.0.1:8889/auction'
DEFAULT_META_PATH = 'meta'
DEFAULT_APP_PATH = 'demoapp'

DATABASE_DEFAULT_SCHEMA_DEFINE = 'demoapp.schema.sql_schema.SQLDBSchema'

# 开发阶段使用的数据库，默认的对数据库的更新都在此
DATABASE_DEFAULT_DEV_URL = 'mysql://root:root@127.0.0.1:8889/auction_dev'
# BDD阶段测试使用的数据库
DATABASE_DEFAULT_TEST_URL = 'mysql://root:root@127.0.0.1:8889/auction_test'