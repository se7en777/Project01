
import re
from netmiko import ConnectHandler, NetMikoAuthenticationException
import sys
import logging
import time



# 配置日志
logging.basicConfig(level=logging.WARNING,format='%(asctime)s - %(levelname)s - %(message)s')
#logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 预定义的用户名和密码
credentials = [
    ('admin1', 'pass1'),
    ('admin2', 'pass2'),
    ('admin3', 'pass3'),
    ('admin4', 'pass4'),
    ('admin5', 'pass5'),
]

def validate_mac(mac_address):
    """
    验证MAC地址格式是否正确
    """
    return re.match("[0-9a-f]{4}\\.[0-9a-f]{4}\\.[0-9a-f]{4}$", mac_address)

def validate_ip(ip_address):
    """
    验证IP地址格式是否正确
    """
    return re.match(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", ip_address)

def get_user_input():
    """
    获取并验证用户输入
    """
    target_mac = input("请输入要查找的MAC地址（格式：xxxx.xxxx.xxxx）: ").lower()
    if not validate_mac(target_mac):
        logger.warning("MAC地址格式不正确，请使用格式：xxxx.xxxx.xxxx")
        sys.exit(1)

    ip = input("请输入交换机的IP地址: ")
    if not validate_ip(ip):
        logger.warning("IP地址格式不正确，请使用格式：xxx.xxx.xxx.xxx")
        sys.exit(1)

    return target_mac, ip

def connect_device(ip, credentials):
    """
    连接到设备并返回连接对象
    """
    for username, password in credentials:
        device = {
            'device_type': 'cisco_ios',
            'ip': ip,
            'username': username,
            'password': password,
        }
        try:
            return ConnectHandler(**device), username, password
        except NetMikoAuthenticationException:
            logger.warning(f"使用 {username}/{password} 登录设备 {ip} 失败，尝试其他凭据...")
    print(f"无法使用提供的凭据连接到设备 {ip}")
    sys.exit(1)

def show_port_config(connection, source_port):
    """
    获取并显示端口的配置
    """
    port_config = connection.send_command(f"show running-config interface {source_port}")
    logger.info(f"{source_port} 的配置为：\n{port_config}")

def find_mac_address(ip, target_mac, username, password, max_hops=10):
    logger.warning(f"开始在设备 {ip} 上查找MAC地址 {target_mac}，剩余跳数：{max_hops}")
    if max_hops == 0:
        logger.warning("达到最大跳数，停止查询。")
        return
    
    device = {
        'device_type': 'cisco_ios',
        'ip': ip,
        'username': username,
        'password': password,
    }
    
    try:
        connection = ConnectHandler(**device)

        # 获取hostname
        hostname_output = connection.send_command("show running-config | include hostname")
        time.sleep(0.5)
        hostname_match = re.search(r"hostname (\S+)", hostname_output)
        hostname = hostname_match.group(1) if hostname_match else ip

        #mac_address_table = connection.send_command(f"show mac address-table address {target_mac}")
        #logger.info(f"show mac address-table address {target_mac}\n {mac_address_table}")
        #time.sleep(0.5)
        
        #mac_table_regex = re.compile(r"\s+\d+\s+" + re.escape(target_mac) + r"\s+\S+\s+(\S+)")
        #match = mac_table_regex.search(mac_address_table)

        #cdp_neighbors = connection.send_command("show cdp neighbors detail")
        
        for i in range(1,4):
            mac_address_table = connection.send_command(f"show mac address-table address {target_mac}")
            logger.info(f"show mac address-table address {target_mac}\n {mac_address_table}")
            time.sleep(0.5)
            
            mac_table_regex = re.compile(r"\s+\d+\s+" + re.escape(target_mac) + r"\s+\S+\s+(\S+)")
            match = mac_table_regex.search(mac_address_table)
            
        
            if match:
                source_port = match.group(1)
                logger.warning(f"在设备 {hostname} IP {ip} 上找到MAC地址 {target_mac}，源端口：{source_port}")
                
                # 获取并显示端口配置
                show_port_config(connection, source_port)
                time.sleep(0.5)

                mac_count_output = connection.send_command(f"show mac address-table interface {source_port}")
                time.sleep(0.5)
                mac_count_regex = re.compile(r"Total Mac Addresses for this criterion: (\d+)")
                mac_count_match = mac_count_regex.search(mac_count_output)
                mac_count = int(mac_count_match.group(1)) if mac_count_match else 0
                
                logger.info(f"接口 {source_port} 下的MAC地址为：\n {mac_count_output}")

                # 检查source_port是否是一个Port-channel接口
                if source_port.lower().startswith("po"):
                    logger.warning(f"当前发现的源接口是{source_port}，现在尝试解析是否为Portchannel接口")

                    # 获取Port-channel下的所有物理接口
                    member_ports = connection.send_command(f"show etherchannel {source_port.replace('Po', '')} port-channel")
                    time.sleep(0.5)
                    # 使用正则表达式提取所有物理接口名称
                    member_port_list = re.findall(r"(Gi\d+/\d+/\d+|Fa\d+/\d+/\d+|Te\d+/\d+/\d+)", member_ports)

                    logger.warning(f"当前的接口是Portchannel接口，成员接口为{member_port_list} \n")

                    # 检查每个物理接口的CDP邻居信息
                    for member_port in member_port_list:
                        cdp_neighbors = connection.send_command(f"show cdp neighbors {member_port} detail")
                        lldp_neighbors = connection.send_command(f"show lldp neighbors {member_port} detail")
                        time.sleep(0.5)
                        # ... [进一步处理CDP邻居信息]
                    source_port = member_port
                else:
                    # 如果source_port不是一个Port-channel接口，直接获取其CDP邻居信息
                    cdp_neighbors = connection.send_command(f"show cdp neighbors {source_port} detail")
                    lldp_neighbors = connection.send_command(f"show lldp neighbors {source_port} detail")
                    time.sleep(0.5)
                break #add break
            else:
                logger.warning(f"在设备 {hostname} IP {ip} 上未找到MAC地址 {target_mac}")
        connection.disconnect()
    except Exception as e:
        logger.error(f"在设备 {hostname} IP {ip} 上查找MAC地址时发生错误：{str(e)}")
        return
    
    cdp_count_regex = re.compile(r"Total cdp entries displayed : (\d+)")
    lldp_count_regex = re.compile(r"Total entries displayed: (\d+)")
    cdp_count_match = cdp_count_regex.search(cdp_neighbors)
    lldp_count_match = lldp_count_regex.search(lldp_neighbors)
    cdp_count = int(cdp_count_match.group(1)) if cdp_count_match else 0
    lldp_count = int(lldp_count_match.group(1)) if lldp_count_match else 0
    
    # 检查是否有思科话机或无线AP
    is_phone_or_ap = re.search(r"Cisco IP Phone|Cisco AP", cdp_neighbors, re.IGNORECASE)
    
    # 如果找到了思科话机或无线AP，记录日志并返回
    if is_phone_or_ap:
        logger.warning(f"在设备 {hostname} IP {ip} 的接口 {source_port}上找到思科话机或无线AP，不认为此接口连接到交换机。")
        cdp_count = 0
        lldp_count = 0

    if mac_count >= 3 or (cdp_count > 0 and lldp_count > 0):
        
        cdp_regex = re.compile(r"Device ID: (.+?)\n.*?IP address: (.+?)\n.*?Platform: (.+?),.*?Interface: (.+?),  Port ID \(outgoing port\): (.+?)\n", re.DOTALL)
        cdp_match = cdp_regex.search(cdp_neighbors)
        
        if cdp_match:
            device_id, ip_address, platform, interface, port_id = cdp_match.groups()
            logger.warning(f"MAC地址 {target_mac} 在设备 {hostname} IP {ip} 的端口 {source_port} 被发现。\n 并且该端口连接到另一个交换机{device_id} IP {ip_address} 端口 {port_id}。\n ")
            logger.info(f"CDP信息如下: \n {cdp_neighbors} \n")

            #continue_search = input(f"是否继续在下一个交换机{device_id} {ip_address}上查询MAC地址？(yes/no): ").strip().lower()
            #if continue_search in ['yes', 'y']:
            #    find_mac_address(ip_address, target_mac, username, password, max_hops=max_hops-1)
            #else:
            #    logger.warning("查询已停止。")
            find_mac_address(ip_address, target_mac, username, password, max_hops=max_hops-1)
        else:
            lldp_regex = re.compile(r"System Name: (.+?)\n.*?Management Addresses:\n    IP: (.+?)\n.*?Local Intf: (.+?)\n.*?Port id: (.+?)\n", re.DOTALL)
            lldp_match = lldp_regex.search(lldp_neighbors)
            
            if lldp_match:
                system_name, ip, local_intf, port_id = lldp_match.groups()
                logger.warning(f"MAC地址 {target_mac} 在设备 {hostname} IP {device["ip"]} 的端口 {source_port} 被发现。\n 并且该端口连接到另一个交换机{device_id} IP {ip} 端口 {port_id}。\n ")
                logger.info(f"LLDP信息如下: \n {lldp_neighbors} \n")
            else:
                logger.warning("未能解析CDP或LLDP邻居信息。")
                logger.warning(f"接口 {source_port} 的CDP邻居信息：\n{cdp_neighbors}")
                logger.warning(f"接口 {source_port} 的LLDP邻居信息：\n{lldp_neighbors}")
    else:
        #logger.warning(f"MAC地址 {target_mac} 直接连接到设备 {ip} 的端口 {source_port}。")
        logger.warning(f"MAC地址 {target_mac} 直接连接到设备{hostname} {ip} 的端口 {source_port}。")

def main():
    target_mac, ip = get_user_input()
    connection, username, password = connect_device(ip, credentials)
    find_mac_address(ip, target_mac, username, password)

if __name__ == "__main__":
    main()

]
