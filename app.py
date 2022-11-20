#! /usr/bin/python
# -*- coding: utf-8 -*-
# Author: kelvinBen
# Github: https://github.com/kelvinBen/AutoRedTools

import os
import re
import sys
import json
import yaml
import click
import shutil
import requests
import subprocess
from requests.adapters import HTTPAdapter
from custom_exception import CustomException
from utils import *
class Main():
    def __init__(self, github_token, github_proxy, tools_path) -> None:
        self.token = github_token
        self.proxy = github_proxy
        self.tools_path = tools_path
        self.ghproxy_flag = False

        self.GHPROXY = "https://ghproxy.com/"
        self.headers = {"Content-Type": "application/json"}
        self.session = requests.session()
        self.session.mount("http://", HTTPAdapter(max_retries=5))
        self.session.mount("https://", HTTPAdapter(max_retries=5))

    def start(self, out_path):
        self.__set_proxy__()
        with open(file=self.tools_path, encoding="utf8") as open_file:
            content = open_file.read()
            try:
                json_list = json.loads(content)
            
                for json_obj in json_list:
                    dir_name = json_obj["dir_name"]
                    dir_path = os.path.join(out_path, dir_name)

                    if not os.path.exists(dir_path):
                        os.makedirs(dir_path)

                    tools_list = json_obj["tools_list"]
                    for tools_name, tools_json_obj in tools_list.items():
                        tools_url = tools_json_obj["url"]
                        tools_type = tools_json_obj["type"]
                        platforms = tools_json_obj["platform"]
                        tools_out_path = os.path.join(dir_path, tools_name)

                        if (not "git version" in os.popen("git version").read()) or (tools_type == "binary"):
                            self.download_code_or_binary(tools_out_path, tools_url, platforms, tools_type)
                        else:
                            self.clone_source_code(tools_out_path, dir_path, tools_url)

            except json.decoder.JSONDecodeError as e:
                msg = re.sub(r'Expecting.*?:',"", str(e)).strip()
                error_msg = ("请检查配置文件: %s 中 %s 的配置是否正确!!!") % (self.tools_path,msg)
                raise(CustomException(error_msg))
            except KeyError as e:
                msg = re.sub(r'KeyError.*?:',"", str(e)).strip()
                error_msg = ("配置文件: %s 中未检索到Key: %s ，请参考配置样例文件后重新输入!!!") % (self.tools_path,msg)
                raise(CustomException(error_msg))
            except Exception as e:
                raise(e)

    def clone_source_code(self, tools_out_path, dir_path, tools_url) -> None:
        '''
            使用Git拉取/更新代码
        '''
        if not os.path.exists(tools_out_path):  # 使用clone拉取主分支代码
            git_url = tools_url + ".git"
            if self.ghproxy_flag:
                git_url = self.GHPROXY + tools_url + ".git"
            os.chdir(dir_path)
            cmd = ['git','clone',git_url] 
            if self.proxy and not self.ghproxy_flag:
                cmd = ['git','clone', git_url,'--config','https.proxy=' + self.proxy]
                
            return_lines = str(subprocess.call(cmd))
            if "Proxy CONNECT aborted" in return_lines:
                error_msg = "请检查git全局配置文件中的代理配置是否正确!!!"
                raise(CustomException(error_msg))

            if "Could not resolve proxy: None" in return_lines:
                error_msg = "请检查git全局配置文件中代理配置是否正确!!!"
                raise(CustomException(error_msg))
            if "Connection reset by peer" in return_lines:
                error_msg="不能访问github.com请使用-p参数配置代理后使用!!!"
                raise(CustomException(error_msg))
            if "Operation timed out" in return_lines:
                error_msg = "请检查是否可以直接通过浏览器访问github.com或者代理配置是否正确!!!"
                raise(CustomException(error_msg))
        else:  # 更新代码到最新版本
            git_dir_path = os.path.join(tools_out_path, ".git")
            if os.path.exists(git_dir_path):
                os.chdir(tools_out_path)
                cmd = ['git','pull'] 
                subprocess.call(cmd)

    def download_code_or_binary(self, tools_out_path, tools_url, platforms, tools_type) -> None:
        try:
            sys_platform = platforms[sys.platform]
        except KeyError as e:
            # 如果是Java版本则下载所有Java版本的
            sys_platform = platforms["java"]
        except Exception as e:
            raise(e)

        if type(sys_platform) == type("str"):
            # 如果是str类型则直接获取工具名称
            file_name = sys_platform
        else:
            cpu_type = get_cpu_type()  # 获取CPU类型
            file_name = sys_platform[cpu_type]

        if "www" in tools_url:
            api_url = tools_url.replace("www", "")
        api_url = tools_url.replace("github.com", "api.github.com/repos") + "/releases/latest"

        try:
            resp = self.__requsets__(api_url)
            repos_json_obj = resp.json()
            tools_vesion = str(repos_json_obj["tag_name"])
            assets_list = repos_json_obj["assets"]
            zipball_url = repos_json_obj["zipball_url"]  # 源代码
            # 文件不存在，创建并下载
            if not os.path.exists(tools_out_path):
                os.makedirs(tools_out_path)

            tools_name = ""
            tools_download_url = zipball_url
            if tools_type == "binary":
                for assets in assets_list:
                    browser_download_url = assets["browser_download_url"]
                    if file_name in browser_download_url:
                        tools_name = assets["name"]
                        tools_download_url = browser_download_url

            # TODO 是否需要更新二进制文件？期待反馈
            self.download_tools(tools_download_url, tools_out_path, tools_name, tools_vesion)
        except KeyError as e:
            # 无发布版本忽略
            return
        except AttributeError as e:
            errmsg= ("访问地址 %s 地址异常，请检查网络或者使用-p参数配置代理后重试!!!" % api_url)
            raise(CustomException(errmsg))
        except Exception as e:
            raise(e)

    def download_tools(self,tools_download_url, tools_out_path, tools_name, tools_vesion) -> None:
        new_file_name = tools_name + "_" + tools_vesion
        if ("." in tools_name):
            new_file_name = tools_name
            if not (tools_vesion in tools_name):
                new_file_name = tools_name[:tools_name.index(".")] + "_" + tools_vesion + tools_name[tools_name.index("."):]

        tools_file_path = os.path.join(tools_out_path, new_file_name)
        print(">>>", tools_download_url, tools_file_path)
        if os.path.exists(tools_file_path):
            return

        resp = self.__requsets__(tools_download_url, True)
        current_download_size = 0  # 已下载大小
        chunk_size = 1024 * 1024 * 5  # 单次5MB大小的下载
        content_length = int(resp.headers["content-length"])
        try:
            print('文件: {} 正在下载中, 总大小为: {size:.2f} MB'.format(tools_name, size=content_length / 1024 / 1024))
            with open(file=tools_file_path, mode="wb") as f:
                for data in resp.iter_content(chunk_size=chunk_size):
                    current_download_size += len(data)
                    f.write(data)
                    print('\r' + '下载进度: %s%.2f%%' % ('=' * int(current_download_size * 50 / content_length), float(current_download_size / content_length * 100)), end=' ')
        except Exception as e:
            raise(e)
    
    def __set_proxy__(self):
        if not self.proxy:
            return
        if "ghproxy.com" in self.proxy:
            self.ghproxy_flag = True
            return

        self.__check_proxy__()

        proxies = {}
        # 配置 requests 代理
        proxies["http"] = self.proxy
        proxies["https"] = self.proxy
        self.session.proxies = proxies

    def __check_proxy__(self) -> bool:
        try:
            proxies = {"http": self.proxy,"https": self.proxy}
            requests.get("https://www.google.com",proxies=proxies)
        except Exception as e:
            error_msg = "检测到使用代理：%s 配置错误，请检查无误后再重试!!!" % (self.proxy)
            raise CustomException(error_msg)
        
    def __requsets__(self, url, stream=False):
        try:
            if self.token:
                self.headers["Authorization"] = ("token %s") % (self.token)

            if stream:
                self.headers["Content-Type"] = "application/octet-stream"

            if self.ghproxy_flag and (not "https://api.github.com" in url):
                url = self.GHPROXY + url

            resp = self.session.get(url, headers=self.headers, stream=stream, timeout=(10, 20))
            if resp.status_code == requests.codes.ok:
                return resp
        except requests.exceptions.ConnectTimeout as e:
            print("链接github.com超时，请使用-p参数设置代理或者在config.yml中设置代理后重试!!!")
        except requests.exceptions.ReadTimeout as e:
            print("读取github.com超时，请使用-p参数设置代理或者在config.yml中配置代理后重试!!!")
        finally:
            resp.close()

def __print_banner__():
    script_root_dir = os.path.dirname(__file__)
    bannerFile = os.path.basename(os.path.join(script_root_dir, "banner.txt"))
    if os.path.exists(bannerFile):
        with open(bannerFile) as f:
            print(f.read())
            print()
    else:
        print("                  _          _____            _  _______             _       ")
        print("     /\          | |        |  __ \          | ||__   __|           | |      ")
        print("    /  \   _   _ | |_  ___  | |__) | ___   __| |   | |  ___    ___  | | ___  ")
        print("   / /\ \ | | | || __|/ _ \ |  _  / / _ \ / _` |   | | / _ \  / _ \ | |/ __| ")
        print("  / ____ \| |_| || |_| (_) || | \ \|  __/| (_| |   | || (_) || (_) || |\__ \ ")
        print(" /_/    \_\\__,_| \__|\___/ |_|  \_\\___| \__,_|   |_| \___/  \___/ |_||___/ ")
        print("                                   https://github.com/kelvinBen/AutoRedTools ")
        print()

def init():
    __print_banner__()
    # 获取并创建用户目录
    user_dir = os.path.expanduser('~')
    doc_dir = os.path.join(user_dir + os.sep + "Documents" + os.sep + "AutoRedTools")
    if not os.path.exists(doc_dir):
        os.makedirs(doc_dir)

    # 复制脚本目录下的全局配置文件到用户目录
    config_path = os.path.join(doc_dir, "config.yml")
    if not os.path.exists(config_path):
        script_config=os.path.join(os.path.dirname(__file__),"config.yml")
        shutil.copyfile(script_config, config_path)
    
    # 复制脚本目录下的工具配置文件到用户目录
    tools_path = os.path.join(doc_dir, "tools.json")
    if not os.path.exists(tools_path):
        script_tools = os.path.join(os.path.dirname(__file__), "tools.json")
        shutil.copyfile(script_tools, tools_path)
    
    # 获取全局配置文件信息
    config_dict = None
    with open(config_path, "r" ,encoding="utf-8") as config_file:
        config_dict = yaml.safe_load(config_file)
    return tools_path,config_dict

@click.command("")
@click.option("-o", "--output", required=True, type=click.Path(exists=False), help="请输入需要安装的工具目录。")
@click.option("-t", "--token", type=str, help="请输入GitHub Token，用于突破GitHub API速率限制")
@click.option("-p", "--proxy", type=str, help="请输入代理地址，用于加速GitHub下载效率，支持http/https/sockt5模式")
def cli(output, token=None, proxy=None):
    try:
        if not os.path.isabs(output):
            output = os.path.join(os.getcwd(), output)

        if not os.path.exists(output):
            os.makedirs(output)
        
        tools_path, config_dict = init()
        github_token = config_dict.get("github_token", None)
        if token:
            github_token = token

        github_proxy = config_dict.get("proxy", None)
        if proxy:
            github_proxy = proxy

        Main(github_token, github_proxy, tools_path).start(output)
    except CustomException as e:
        print(e)
    except Exception as e:
        raise(e)

if __name__ == "__main__":
    cli()
