import os
import time
import json
import yaml
import base64
import requests
import re
import paramiko
from db import get_db


from datetime import datetime




def get_token():
    text = 'admin:Pwd123456'
    return "Basic " + base64.b64encode(text.encode()).decode()


headers = {
    'Content-Type': 'application/json',
    'Authorization': get_token()
}

mydb = get_db()

# def get_envs():
#     return Environments

def get_k8cfg(ip):
    ssh = paramiko.SSHClient()
    know_host = paramiko.AutoAddPolicy()
    ssh.set_missing_host_key_policy(know_host)
    # print(ip)
    ssh.connect(hostname=ip, port=22, username='root', password='caicloud2020')  # 来一个超时机制，用做换密码为2020登录
    # print(f'after {ip} connect')
    stdin, stdout, stderr = ssh.exec_command('cat ~/.kube/config')
    cfg_info = stdout.read().decode('utf-8')

    return cfg_info
    # pass

def get_cluster():
    # cur = mydb.env.find({})             # 从 env 读取环境
    # env_vip_list = {i: for i['vip'],j['env'] in cur}

    cur = mydb.env.find({})  # 从 env 读取环境
    env_list = {i['env']: i['vip'] for i in cur}

    print(env_list)

    cluster_info = []

    for env, vip in env_list.items():
        url = f'http://{vip}:6060/hodor/apis/admin.cluster.caicloud.io/v2alpha1/clusters'
        res = requests.get(url=url, headers=headers)
        data = res.json()

        for i in data['items']:
            tmp = {}
            tmp['env_name'] = env
            tmp['env_vip'] =  vip
            tmp['id'] =  i['metadata']['id']
            tmp['alias'] =  i['metadata']['alias']
            cluster_info.append(tmp)


    master_ips = {}
    master_ips['date'] = str(datetime.date(datetime.now()))
    master_ips['data'] = []
    # print(cluster_info)

    for data in cluster_info:
        ip = get_master_ip(data['env_vip'], data['id'])
        cfg = get_k8cfg(ip)

        tmp = {
            'env_vip' : data['env_vip'],
            'env_name': data['env_name'],

            'cfg' : cfg,
            'id': data['id'],
            'alias': data['alias'],
            'cluster_ip': ip
        }

        master_ips['data'].append(tmp)
    # print(master_ips)
    # time.sleep(100)

    mydb.cluster.delete_many({})
    mydb.cluster.insert_one(master_ips)



def get_master_ip(env_ip, cluster_id):
    # vip = '192.168.129.30'
    # cluster_id = 'user-a33684-20200823071257-1d3s'
    # cluster_id = 'compass-stack'
    # cluster_id = 'user-c40e5c-20200823071127-pww'
    url = f'http://{env_ip}:6060/hodor/apis/admin.cluster.caicloud.io/v2alpha1/clusterauths/{cluster_id}'
    res = requests.get(url=url, headers=headers)
    # print(res.json())
    # print(res.text)
    data = res.json()
    return data['endpointIP']
    # pass


def get_cfg_yaml():
    with open('env.yaml', 'r') as f:
        f_data = f.read()
        data = yaml.safe_load(f_data)
    return data


def get_daily_info(env ,cluster):
    with open(f'daily_info/{env}/{cluster}.json') as f:
        data = json.load(f)
    return data

def get_duty():
    cur = mydb.user.find({})
    data = [i for i in cur]

    # print(data)
    component_duty = {}
    for i in data:
        for j in i['component']:
            component_duty[j] = i['user_name']

    # print(component_duty)
    return component_duty


if __name__ == '__main__':
    # get_daily_info('2.11-rc4', 'compass-stack',)
    # get_cluster()
    # get_cfg()
    get_cluster()
    # read_cfg()
    # get_duty()
    pass

'''


'''