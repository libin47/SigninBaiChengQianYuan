# -*- coding: utf-8 -*-
import logging
import os
import time
from ..SQL.setting import LOG_DATA
dir = os.path.split(__file__)[0]


try:
    os.mkdir(os.path.join(dir, '../log'))
except:
    pass


# 创建单独日志
class logger(object):
    def __init__(self, province_id):
        logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s] %(levelname)s: %(message)s',
                        datefmt='%Y/%m/%d/%H:%M:%S',
                        )
        file = logging.StreamHandler(open(os.path.join(dir, '../log/%s.log'%province_id), 'w', encoding='utf8'))
        file.setLevel(logging.DEBUG)
        file.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
        logger = logging.getLogger('province%s'%province_id)
        logger.addHandler(file)
        self.logger = logger
        self.province_id = province_id
        LOG_DATA.set(str(self.province_id), '')

    def savedb(self, msg, type='INFO'):
        old_log = LOG_DATA.get(str(self.province_id))
        prmsg = '[%s] %s: %s'%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), type, msg)
        new_log = old_log + '\n' + prmsg
        LOG_DATA.set(str(self.province_id), new_log)

    def info(self, msg):
        self.savedb(msg, 'INFO')
        self.logger.info(msg)

    def warning(self, msg):
        self.savedb(msg, 'WARNING')
        self.logger.warning(msg)

    def error(self, msg):
        self.savedb(msg, 'ERROR')
        self.logger.error(msg)

    def debug(self, msg):
        self.savedb(msg, 'DEBUG')
        self.logger.debug(msg)