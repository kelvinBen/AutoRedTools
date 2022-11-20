#! /usr/bin/python
# -*- coding: utf-8 -*-
# Author: kelvinBen
# Github: https://github.com/kelvinBen/AutoRedTools

import os
import sys
import platform

def get_cpu_type():
    sys_platform = sys.platform
    if sys_platform == "darwin":
        cpu_type = os.popen("sysctl machdep.cpu.brand_string").read().replace("machdep.cpu.brand_string:", "").strip()
        if "Apple" in cpu_type:
            return "arm64"
        else:
            return "amd64"
    else:
        return platform.machine()