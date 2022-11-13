#! /usr/bin/python
# -*- coding: utf-8 -*-
# Author: kelvinBen
# Github: https://github.com/kelvinBen/AutoRedTools

# 本工具基于GitHub API，未配置GitHub Token会被GitHub限制，导致部分软件下载失败
# 配置GitHub Token
# 配置方法：https://docs.github.com/cn/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
github_token=None

# 配置代理, 由于某些原因GitHub访问速度较慢，配置代理用于加速GitHub的访问
proxy=None