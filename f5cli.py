#!/usr/bin/env  python
# -*- coding: utf-8 -*-
"""
 File Name：  f5cli
 Description :
 Author :  seven
 date：   2018/11/9
 Change Activity:
     2018/11/9:
"""

# 导包
import pandas as pd
import re


# 定义一个函数，用于判断字符串是否是IPv4格式
def is_ipv4(address):
    compile_ip = re.compile(
        '^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
    if compile_ip.match(address):
        return True
    else:
        return False


# 定义一个函数，用于判断isp名称是否格式正确
def is_isp(isp_name):
    giantisp = re.compile('^CT\d$|^CU\d$|^CM\d$')
    if giantisp.match(isp_name):
        return True
    else:
        return False

# 尝试读取程序同目录下的f5.csv文件到DataFrame
try:
    data = pd.read_csv('./f5.csv')
    print('文件读取成功，文件内容格式检查中...')

    # 文件可读，继续，重命名列
    data.columns = ['serverip', 'port', 'protocol', 'isp', 'mappedip', 'mappedport']
    # 判断文件的行数和列数是否符合要求，如果不符合要求，给出提示
    if (data.columns.size != 6) or (len(data) < 1):
        print('文件内容格式错误，文件至少有一行内容，且需要含有以下几列： \n 原始IP地址,原始端口,协议,线路名称,映射后IP地址,映射后端口')
    else:   #如果符合要求，继续
        # 初始化错误计数器,错误列表
        err_count = 0
        err_list = []
        # 遍历dataframe 取值
        for index, row in data.iterrows():
            serverip = row['serverip']
            port = row['port']
            protocol = row['protocol']
            isp = row['isp']
            mappedip = row['mappedip']
            mappedport = row['mappedport']
            # 尝试把端口号转换成int格式，转不了没关系，后面会处理
            try:
                port = int(row['port'])
            except:
                pass
            try:
                mappedport = int(row['mappedport'])
            except:
                pass
            # 检查各列的值是否符合格式，不符合计数器+1，定位错误所在行数并将错误内容写到列表
            if is_ipv4(serverip) is False:
                err_count += 1
                err_row_no = data[data.serverip == serverip].index.tolist()
                err_value = '第{row_no}行中的"{err}"格式错误。'.format(row_no=err_row_no[0] + 1, err=serverip)
                err_list.append(err_value)
            if is_ipv4(mappedip) is False:
                err_count += 1
                err_row_no = data[data.mappedip == mappedip].index.tolist()
                err_value = '第{row_no}行中的"{err}"格式错误。'.format(row_no=err_row_no[0] + 1, err=mappedip)
                err_list.append(err_value)
            if (type(port) != int) or ((0 < port < 65535) is False):
                err_count += 1
                err_row_no = data[data.port == port].index.tolist()
                err_value = '第{row_no}行中的"{err}"格式错误。'.format(row_no=err_row_no[0] + 1, err=port)
                err_list.append(err_value)
            if (type(mappedport) != int) or ((0 <= mappedport <= 65535) is False):
                err_count += 1
                err_row_no = data[data.mappedport == mappedport].index.tolist()
                err_value = '第{row_no}行中的"{err}"格式错误。'.format(row_no=err_row_no[0] + 1, err=mappedport)
                err_list.append(err_value)
            if protocol not in ('tcp', 'udp', 'TCP', 'UDP'):
                err_count += 1
                err_row_no = data[data.protocol == protocol].index.tolist()
                err_value = '第{row_no}行中的"{err}"格式错误。'.format(row_no=err_row_no[0] + 1, err=protocol)
                err_list.append(err_value)
            if is_isp(isp) is False:
                err_count += 1
                err_row_no = data[data.isp == isp].index.tolist()
                err_value = '第{row_no}行中的"{err}"格式错误。'.format(row_no=err_row_no[0] + 1, err=isp)
                err_list.append(err_value)
        #如果有错误，报错结束
        if err_count != 0:
            print('检查完毕，共有' + str(err_count) + '个参数格式错误：')
            for err in err_list:
                print(err)
        #如果没有错误，继续
        else:
            print('检查完毕，所有参数格式正确。')
            pool_cli = []
            vs_cli = []
            #遍历dataframe 取值 将格式化的命令写入列表
            for index, row in data.iterrows():
                serverip = row['serverip']
                port = row['port']
                protocol = row['protocol']
                isp = row['isp']
                mappedip = row['mappedip']
                mappedport = row['mappedport']
                #定义命名规则的格式
                mapped_host = mappedip.split('.', 2)[-1]
                svr_host = serverip.split('.', 2)[-1]
                node_name = 'N_S_%s' % svr_host
                pool_name = 'P_S_%s-%s' % (svr_host, port)  # 格式化成想要的pool_name
                vs_name = 'VS_Inbound_%s_%s_%s%s' % (isp, mapped_host, protocol.upper(), mappedport)
                #定义最终cli命令输出的格式
                createpool = 'create ltm pool {pool_name} {{ members add {{ {node_name}:{port} {{ address {node_ip} }} }}  monitor {monitor} }}'.format(
                    pool_name=pool_name, node_name=node_name, port=port, node_ip=serverip, monitor=protocol)
                createvs = 'create ltm virtual {vs_name} {{ destination {mappedip}:{mappedport} ip-protocol {protocol} mask 255.255.255.255 pool {pool_name} profiles add {{ fastL4 {{ }} }} rules {{ iR_LAN_Access_SNAT }} source 0.0.0.0/0 }} '.format(
                    vs_name=vs_name, isp=isp, mappedip=mappedip, mappedport=mappedport, protocol=protocol,
                    pool_name=pool_name)
                pool_cli.append(createpool)
                vs_cli.append(createvs)
            #尝试写入文件
            try:
                pool_file = open('pool.txt', 'w')
                vs_file = open('vs.txt', 'w')
                for pool in pool_cli:
                    print(pool, file=pool_file)
                for vs in vs_cli:
                    print(vs, file=vs_file)
                print('运行结果保存在程序目录下的pool.txt和vs.txt文件中。\nSSH登录F5，输入‘tmsh’进入命令行配置模式 \n先输入pool.txt中的命令创建好Node和Pool,再输入vs.txt中的命令创建Virtual Server。')
            except FileNotFoundError:
                print('要找的文件不存在')
            except:
                print('未知错误')
            finally:
                pool_file.close()
                vs_file.close()

except FileNotFoundError:
    print('文件读取失败，请检查f5.csv是否存在于程序所在目录！')
except:
    print('文件读取失败，未知错误！')
finally:
    print('程序运行结束，有问题请反馈。')
