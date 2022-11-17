#! /usr/bin/python
# -*- coding: utf-8 -*-
# Author: kelvinBen
# Github: https://github.com/kelvinBen/AutoRedTools

import os
import sys
import json
import requests
import platform
import getopt
import config

from contextlib import closing

proxies = {}
headers = {
    "Content-Type": "application/json"
}

def __set_proxy__(proxy):
    if proxy or config.proxy:
        # 配置 requests 代理
        proxies["http"] = proxy
        proxies["https"] = proxy
        # 配置git代理
        os.system("git config --global http.https://github.com.proxy %s" % (proxy))
        os.system("git config --global https.https://github.com.proxy %s" % (proxy))

    
def start(out_path, proxy, token) -> None:
    __set_proxy__(proxy) # 启动代理
    if token or config.github_token:
        headers["Authorization"] = ("token %s") % (token)

    if not os.path.exists(out_path):
        os.makedirs(out_path) # 创建输出目录

    with open(file="tools.json",encoding="utf8") as open_file:
        content = open_file.read()
        json_list = json.loads(content)

        for json_obj in json_list:
            dir_name = json_obj["dir_name"]
            dir_path = os.path.join(out_path, dir_name)

            if not os.path.exists(dir_path):
                os.makedirs(dir_path) # 创建分类目录
            
            tools_list = json_obj["tools_list"]
            for tools_name, tools_json_obj in tools_list.items():
                tools_url = tools_json_obj["url"]
                tools_type = tools_json_obj["type"]
                platforms = tools_json_obj["platform"]
                tools_path = os.path.join(dir_path, tools_name)

                if (not "git version" in os.popen("git version").read()) or (tools_type == "binary"):
                    download_code_or_binary(tools_path, tools_url, platforms, tools_type)
                else:
                    clone_source_code(tools_path, dir_path, tools_url)

def clone_source_code(tools_path, dir_path, tools_url) -> None:
    '''
        使用Git拉取/更新代码
    '''
    if not os.path.exists(tools_path): # 使用clone拉取主分支代码
        git_url = tools_url + ".git"
        os.chdir(dir_path)
        os.system(("git clone %s") % git_url)
    else: # 更新代码到最新版本
        git_dir_path = os.path.join(tools_path, ".git")
        if os.path.exists(git_dir_path):
            os.chdir(tools_path)
            os.system("git pull")

def download_code_or_binary(tools_path, tools_url, platforms, tools_type) -> None:
    try:
        sys_platform = platforms[sys.platform] 
    except KeyError as e:  
        # 下载所有适配的版本
        sys_platform = platforms["java"]
    
    if type(sys_platform) == type("str"):
        file_name = sys_platform
    else:
        cpu_type = get_cpu_type() # 获取CPU类型
        file_name = sys_platform[cpu_type]

    if "www" in tools_url:
        api_url = tools_url.replace("www", "")
    api_url = tools_url.replace("github.com", "api.github.com/repos") + "/releases/latest"
    
    with closing(requests.get(url=api_url, proxies=proxies)) as resp:
        if not (resp.status_code == requests.codes.ok):
            return

        repos_json_obj = resp.json()
        try:
            tools_vesion = str(repos_json_obj["tag_name"])
            assets_list = repos_json_obj["assets"]
            zipball_url = repos_json_obj["zipball_url"] # 源代码
        except KeyError as e: 
            # 未发布正式版本就忽略
            return

        # 文件不存在，创建并下载
        if not os.path.exists(tools_path):
            os.makedirs(tools_path)
        tools_name = ""
        tools_download_url = zipball_url
        if tools_type == "binary":
            for assets in assets_list:
                browser_download_url = assets["browser_download_url"]
                if file_name in browser_download_url:
                    tools_name = assets["name"]
                    tools_download_url = browser_download_url

        # TODO 是否需要更新二进制文件？期待反馈
        download_tools(tools_download_url, tools_path, tools_name, tools_vesion)
        
def download_tools(tools_download_url, tools_path, tools_name, tools_vesion) -> None:
    new_file_name = tools_name + "_" + tools_vesion
    if ("." in tools_name):
        new_file_name = tools_name
        if not(tools_vesion in tools_name):   
            new_file_name = tools_name[:tools_name.index(".")] + "_" + tools_vesion + tools_name[tools_name.index("."):]

    tools_file_path = os.path.join(tools_path,new_file_name)
    print(">>>",tools_download_url,tools_file_path)
    if os.path.exists(tools_file_path):
        return
    
    with closing(requests.get(tools_download_url, proxies=proxies, stream=True)) as resp:
        current_download_size = 0 # 已下载大小
        chunk_size = 1024 * 1024 * 5 # 单次5MB大小的下载
        content_length =  int(resp.headers["content-length"])
        try:
            if resp.status_code == requests.codes.ok:
                print('文件: {} 正在下载中, 总大小为: {size:.2f} MB'.format(tools_name, size = content_length / 1024 / 1024))
                with open(file=tools_file_path,mode="wb",encoding="utf8") as f:
                    for data in resp.iter_content(chunk_size=chunk_size):
                        current_download_size += len(data)
                        f.write(data)
                        print('\r' + '下载进度: %s%.2f%%' % ('=' * int(current_download_size * 50 / content_length), float(current_download_size / content_length * 100)), end=' ')
        except Exception as e:
            pass
        finally:
            resp.close()

def get_cpu_type():
    sys_platform = sys.platform
    if sys_platform == "darwin":
        cpu_type = os.popen("sysctl machdep.cpu.brand_string").read().replace("machdep.cpu.brand_string:","").strip()
        if "Apple" in cpu_type:
            return "arm64"
        else:
            return "x86_64"
    else:
        return platform.machine()

def help():
    print("usage: ")
    print("  app.py [option] ... [-o out | -t thread | -p proxy")
    print()
    print("Options and arguments (and corresponding environment variables):")
    print("  -o out:    存在工具集的文件路径，必填项")
    print("  -t token:  配置GitHub Token, 由于本工具使用GitHub API获取，未登录时有速率限制，需要配置GitHub的Token")
    print("  -p proxy:  设置代理池，用于加速访问GitHub提升下载效率，支持http/https/sockt5，非必填项")
    print("  -h help:   使用帮助文档")
    print()
    print("example: ")
    print("  基本使用方法: ")
    print("      python app.py -o ~/Documents/tools")
    print("  配置GitHub Token: ")
    print("      python app.py -o ~/Documents/tools -t xxxxxxxxxxxxxxxxxxxxx")
    print("  使用http代理: ")
    print("      python app.py -o ~/Documents/tools -p http://127.0.0.1:7890")
    print("  使用https代理: ")
    print("      python app.py -o ~/Documents/tools -p https://127.0.0.1:7890")
    print("  使用socks5代理:")
    print("      python app.py -o ~/Documents/tools -p socks5://127.0.0.1:7890")
    exit()

if __name__ == "__main__":
    try:
        opts,args = getopt.getopt(sys.argv[1:], "o:t:p:h",["out=","thread=","proxy=","help"])
    except getopt.GetoptError as e:
        help()
        
    if len(opts) == 0:
        help()

    out_path = ""
    proxy = None
    token = None
    for opt,arg in opts:
        if (opt =="-o" or opt=="--out") and arg:
            out_path = arg
        elif (opt =="-t" or opt=="--token") and arg:
            token = arg
        elif (opt =="-p" or opt=="--proxy") and arg:
            proxy = arg
        else:
            help()
    start(out_path, proxy, token)


   
