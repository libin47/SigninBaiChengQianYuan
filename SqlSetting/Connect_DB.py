# -*- coding: UTF-8 -#-
from sqlalchemy import create_engine


class ConnectDB:
    def __init__(self, host='192.168.2.174', port=3306, user='root', pw='123456', db_name=None):
        self.connect = r'mysql+pymysql://{username}:{password}@{host}:{port}/{databases}?charset={c_set}'.format(
            username=user, password=pw, host=host, port=port, databases=db_name, c_set='utf8')


def set_engine(host='127.0.0.1', port=3306, user='root', pw='123456', db_name=None):
    return create_engine(ConnectDB(host, port, user, pw, db_name).connect, echo=True)

