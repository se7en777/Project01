#!/usr/bin/env  python3
# -*- coding: utf-8 -*-
"""
 File Name：  spider01
 Author :  seven
 Change Activity:
     2018/11/12:
"""
# # 使用getproxy获取代理并检查可用性

# 导入包之前，先monkey patch
# 参考https://github.com/gevent/gevent/issues/1016 否则会报SSL错误
# import gevent.monkey
# gevent.monkey.patch_all()

# https://github.com/fate0/getproxy



import gevent.monkey
gevent.monkey.patch_all()

from getproxy import GetProxy
g = GetProxy()

# 1. 初始化，必须步骤
g.init()

# 2. 加载 input proxies 列表
g.load_input_proxies()

# 3. 验证 input proxies 列表
g.validate_input_proxies()

# 4. 加载 plugin
g.load_plugins()

# 5. 抓取 web proxies 列表
g.grab_web_proxies()

# 6. 验证 web proxies 列表
g.validate_web_proxies()

# 7. 保存当前所有已验证的 proxies 列表
g.save_proxies()


try:
	valid_file = open('valid_proxys.txt', 'w')
	for valid_proxies in g.valid_proxies:
		print(valid_proxies, file=valid_file)
	print(
		'有效代理服务器保存在程序目录下的valid_proxys.txt文件。')
except FileNotFoundError:
	print('文件不存在。')
except:
	print('未知错误。')
finally:
	valid_file.close()

