# -*- coding: utf-8 -*-
import os
from .creat_base import *


def try_creat_rule_table(log):
    if not check_tables():
        log.debug("重建rule表")
        init_data()

