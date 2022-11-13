![License](https://img.shields.io/badge/Version-V1.0.0-red) ![Language](https://img.shields.io/badge/Language-Python3-blue) ![License](https://img.shields.io/badge/License-GPL3.0-orange) [![HitCount](https://hits.dwyl.com/kelvinBen/kelvinBen/AutoRedTools.svg?style=flat&show=unique)](http://hits.dwyl.com/kelvinBen/kelvinBen/AutoRedTools)

## AutoRedTools

AutoRedTools是一款轻量级一站式自动下载/自动更新安全从业人员常用开源的工具，帮助安全从业者快速进行渗透工具的下载以及更新，节约大量环境安装和更新时间。

(注：本工具使用GitHub API能力，需要配置GitHub Token，未配置GitHub Token会被GitHub限制IP访问)

## 前言

- 本项目的开发者目前为个人开发者同时有自己的工作，新的功能或者需求会在闲暇时间进行开发，BUG会优先进行处理。
- 如果在使用中遇到问题或者有新的需求，请在提交BUG反馈，提交BUG前请先阅读最后的"常见问题"。
- 如果您觉得这个项目对您有用，请点击本项目右上角的"star"按钮。
- 如果您想持续跟进新的版本情况，请点击本项目右上角的"Watch"按钮。
- 如果您想参与本项目的开发，请点击本项目右上角的"Fork"按钮,否则请勿点击"Fork"按钮。

## 免责声明

请勿将本项目技术或代码应用在恶意软件制作、软件著作权/知识产权盗取或不当牟利等非法用途中。实施上述行为或利用本项目对非自己著作权所有的程序进行数据嗅探将涉嫌违反《中华人民共和国刑法》第二百一十七条、第二百八十六条，《中华人民共和国网络安全法》《中华人民共和国计算机软件保护条例》等法律规定。本项目提及的技术仅可用于私人学习测试等合法场景中，任何不当利用该技术所造成的刑事、民事责任均与本项目作者无关。

## 适用场景

- 渗透测试环境重装时
- CTF比赛前需要环境安装时
- 攻防比赛时特定系统的环境安装
- 渗透环境需要更新时

## 环境说明

- Python3及以上版本
- GitHub Token

## 使用方法

### 基本使用方法

```bash
    git clone https://github.com/kelvinBen/AutoRedTools
    python app.py -o ~/Documents/tools
```

### 参数说明（app.py）

```TXT
    -o 指定工具安装路径
    -p 指定代理，用于加速工具下载
    -t 设置GitHub Token，未登录GitHub时，每小时只能请求60次，可能会导致部分工具下载失败，建议配置
```

### 配置文件（config.py）

```python
    # 本工具基于GitHub API，未配置GitHub Token会被GitHub限制，导致部分软件下载失败
    # 配置GitHub Token
    # 配置方法：https://docs.github.com/cn/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
    github_token=None

    # 配置代理, 由于某些原因GitHub访问速度较慢，配置代理用于加速GitHub的访问
    proxy=None
```

### 其他使用方法

```TXT
    1. 设置GitHub Token
    python app.py -o ~/Documents/tools -t xxxxxxxxx

    2. 使用http代理的方式启动
    python app.py -o ~/Documents/tools -p http://127.0.0.1:7890
    
    3. 使用https代理的方式启动
    python app.py -o ~/Documents/tools -p https://127.0.0.1:7890

    4. 使用socks5代理的方式启动
    python app.py -o ~/Documents/tools -p socks5://127.0.0.1:7890
```

## 已支持工具列表

### 信息收集工具

[x] AppInfoScanner
[x] OneForAll
[x] Kunyu
[x] Glass
[x] scaninfo
[x] ksubdomain
[x] EmailAll
[x] subDomainsBrute

### 漏洞扫描

[x] xray
[x] Kunpeng
[x] FuYao
[x] afrog
[x] vulmap

### 内网工具

[x] frp
[x] LadonGo

### 免杀提权

[x] nim_shellloader

### 漏洞验证

[x] sqlmap

### CTF

[x] pwntools

### 插件辅助

[x] HaE

### WebShell

[x] Behinder
[x] Godzilla
[x] AntSword
[x] AntSword-Loader

## 自定义工具列表(tools.json)

tools.json 为常用开源软件的下载配置文件。

```TXT
文件结构如下，以xray为例：

[
    {
        "dir_name": "漏洞扫描", 
        "tools_list": {
        "xray": {
            "url": "https://github.com/chaitin/xray",
            "type": "binary",
            "platform": {
                "win32": {
                    "i386": "xray_windows_386.exe",
                    "x86_64": "xray_windows_amd64"
                },
                "darwin": {
                    "x86_64": "xray_darwin_amd64",
                    "arm64": "xray_darwin_arm64"
                },
                "linux": {
                    "i386": "xray_linux_386",
                    "x86_64": "xray_linux_amd64",
                    "arm64": "xray_linux_arm64"
                }
            }
        },
    }
]

dir_name: 为工具的第一级目录，固定写法
tools_list: 为一级目录下的工具集合，固定写法
xray：为工具的名称，非固定写法，可以根据需下载的工具进行命名
url: 为工具的GitHub主地址，固定写法
type: 为工具的类型，目前支持2种模式，source为源代码模式，binary为二进制模式，固定写法
platform: 为需要下载的系统平台，当type为source时需要为{}
    win32： Windows的系统
    darwin: MacOS的系统
    linux： Linux的系统
    java: 使用java编译的工具

    i386： x86架构的系统
    x86_64： X64架构的系统
    arm64： arm64架构的系统
```

## 效果展示

[!效果展示](%E6%95%88%E6%9E%9C%E5%B1%95%E7%A4%BA.png)

## 联系作者

微信：bromomo (添加好友请备注：ART)
微信群：(如过期请通过以上方式添加微信)
[!加群](%E5%8A%A0%E7%BE%A4.jpeg)

需求提交、BUG反馈、软件新增、分类建议均可添加好友或者入群交流。

## Stargazers over time

[![Stargazers over time](https://starchart.cc/kelvinBen/AutoRedTools.svg)](https://starchart.cc/kelvinBen/AutoRedTools)
