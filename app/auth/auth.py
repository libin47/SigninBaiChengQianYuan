# -*- coding: utf-8 -*-
"""
@Author:waiwen
@Time: 2019/12/16 16:55
@Email: iwaiwen@163.com
@Software: PyCharm
@File    : auth.py
"""


class Auth(object):

    def __init__(self, id=None, username=None, password=None):
        self.id = id
        self.username = username
        self.password = password

    def todict(self):
        return self.__dict__

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
