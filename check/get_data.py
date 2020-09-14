import time
import base64
import requests
import paramiko
from datetime import datetime

from db import get_db
from send_to_lark import send


def get_token():
    text = 'admin:Pwd123456'
    return "Basic " + base64.b64encode(text.encode()).decode()


def get_k8cfg(ip):
    ssh = paramiko.SSHClient()
    know_host = paramiko.AutoAddPolicy()
    # 允许连接不在know_hosts文件中的主机
    ssh.set_missing_host_key_policy(know_host)
    try:
        ssh.connect(hostname=ip, port=22, username='root', password='caicloud2020', timeout=5)  # 来一个超时机制，用做换密码为2020登录
    except Exception:
        print(f"ssh {ip} failed")
        return None
    else:
        print(f"ssh {ip} success")
        stdin, stdout, stderr = ssh.exec_command('cat ~/.kube/config')
        cfg_info = stdout.read().decode('utf-8')
        return cfg_info
    # pass

def get_cluster():
    # cur = MYDB.env.find({})             # 从 env 读取环境
    # env_vip_list = {i: for i['vip'],j['env'] in cur}

    cur = MYDB.env.find({})  # 从 env 读取环境
    try:
        env_list = {i['env']: i['vip'] for i in cur}
        # print(env_list)
    except Exception:
        # print("env is empty")
        pass

    else:
        cluster_info = []
        for env, vip in env_list.items():
            url = f'http://{vip}:6060/hodor/apis/admin.cluster.caicloud.io/v2alpha1/clusters'
            res = requests.get(url=url, headers=headers)
            data = res.json()

            for i in data['items']:
                tmp = {}
                tmp['env_name'] = env
                tmp['env_vip'] = vip
                tmp['id'] = i['metadata']['id']
                tmp['alias'] = i['metadata']['alias']
                cluster_info.append(tmp)

        master_ips = {}
        master_ips['date'] = str(datetime.date(datetime.now()))
        master_ips['data'] = []
        # print(cluster_info)

        for data in cluster_info:
            ip = get_master_ip(data['env_vip'], data['id'])
            if not ip:      # 获取集群的 master 节点 ip 失败。
                print(f"can not get master ip of {data['alias']}")
                continue

            cfg = get_k8cfg(ip)
            if not cfg:  # ssh失败 没有拿到配置文件
                continue

            tmp = {
                'env_vip': data['env_vip'],
                'env_name': data['env_name'],
                'cfg': cfg,
                'id': data['id'],
                'alias': data['alias'],
                'cluster_ip': ip
            }

            master_ips['data'].append(tmp)

        MYDB.cluster.delete_many({})
        MYDB.cluster.insert_one(master_ips)


def get_master_ip(env_ip, cluster_id):
    """
    根据环境 ip 和 cluster_id 获得 cluster_ip
    """
    try:
        url = f'http://{env_ip}:6060/hodor/apis/admin.cluster.caicloud.io/v2alpha1/clusterauths/{cluster_id}'
        res = requests.get(url=url, headers=headers)
        data = res.json()
        return data['endpointIP']

    except Exception:
        return None


def get_duty():
    cur = MYDB.user.find({})
    data = [i for i in cur]

    component_duty = {}
    for i in data:
        for j in i['component']:
            component_duty[j] = i['user_name']

    return component_duty

def get_today_duty_list(is_manul=False):
    open_id_list = []
    # print(Duty_today)
    duty_today_add(is_manul)

    if Duty_today:
        for i in Duty_today:
            user0 = MYDB.user.find({"user_name":i})[0]
            open_id_list.append(user0['open_id'])

        msg = ""
        for i in open_id_list:
            fmt = f'<at user_id="{i}"></at>'
            msg += fmt
        msg = f"你负责的组件有异常了\n {msg}"
        Duty_today.clear()
    else:
        msg = "组件运行正常"
    front_url = 'http://192.168.130.29:3000/pod-check/'
    time1 = str(datetime.date(datetime.now()))
    if is_manul:
        time1 = '2020-01-01'
    msg = f"{msg}\n{front_url}{time1}"
    send(msg, is_manul)


def get_duty_man(pod_name):
    """
    alerting-controller-controller-v1-0-5c889b95f5-mqblg
    network-agent-nwmh2
    """
    # pod_name = "alerting-controller-controller-v1-0-5c889b95f5-mqblg"
    component_name_list = pod_name.split('-')
    pod_name_list = "-".join(component_name_list[0:3]),"-".join(component_name_list[0:2]),"-".join(component_name_list[0:1])

    for pod in pod_name_list:
        if pod in Duty:
            # print(Duty[pod])
            return Duty[pod]


def duty_today_add(is_manul=False):
    time1 = str(datetime.date(datetime.now()))
    # MYDB.user
    if is_manul:
        time1 = '2020-01-01'
    cur = MYDB.pod.find({'check_time':time1})
    pod_data = [i for i in cur]
    if pod_data:
        for i in pod_data:
            if i['is_issue'] == True:
                Duty_today.add(i['duty'])

    print(Duty_today)

    # time.sleep(1000)
    # Duty_today.add(name)


MYDB = get_db()
Duty = get_duty()
Duty_today = set()
headers = {
    'Content-Type': 'application/json',
    'Authorization': get_token()
}


if __name__ == '__main__':
    # get_cluster()get_
    get_today_duty_list(is_manul=True)