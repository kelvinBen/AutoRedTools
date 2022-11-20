#! /usr/bin/python
# -*- coding: utf-8 -*-
# Author: kelvinBen
# Github: https://github.com/kelvinBen/AutoRedTools
class CustomException(Exception):
    def __init__(self, error_msg):
        super().__init__(self)
        self.error_msg = error_msg
    def __str__(self):
        return self.error_msg