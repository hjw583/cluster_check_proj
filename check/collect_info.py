import time
import os
import json
import uuid
from datetime import datetime
from kubernetes import client, config

from db import get_db
from get_data import get_duty_man, get_cluster


class ClusterInspect:
    def __init__(self,env_name, env_ip, cluster_name, cluster_ip, is_manul):
        self.env_name = env_name
        self.env_ip = env_ip
        self.cluster_name = cluster_name
        self.cluster_ip = cluster_ip
        self.is_manul = is_manul
        self.nodes_info = []
        self.pods_info = []
        self.namespaces = []
        self.v1 = client.CoreV1Api()
        self.db = get_db()

        # self.all_info = {'cluster_name': self.cluster_name}

    def get_nodes_info(self):
        # 执行kubectl查询命令的是master节点，原来从vip进的就是负载均衡后的master节点 现在获得的是所有的node节点
        # 如何判定node是否正常 -oyaml 里没有很明确
        # self.nodes = [i.status.addresses[0].address for i in self.v1.list_node().items]
        nodes = self.v1.list_node().items
        for node in nodes:
            node_info = {}
            node_info['name'] = node.metadata.name
            node_info['ip']= node.status.addresses[0].address
            node_info['condition'] = node.status.conditions[-1].type
            self.nodes_info.append(node_info)

        time1 =  str(datetime.date(datetime.now()))
        if self.is_manul:
            time1 = time1.replace('2020','2019')
        # self.all_info['nodes_info'] = self.nodes_info
        db_nodes_info = {
                         'env': self.env_ip,
                         'cluster_name': self.cluster_name,
                         'check_time':  time1,        # 2020-09-01
                         'nodes_info': self.nodes_info
                        }

        self.db.node.insert_one(db_nodes_info)
        # print('xx')


    def get_pods_info(self):
        time1 = str(datetime.date(datetime.now()))
        pods = self.v1.list_pod_for_all_namespaces()
        ns_list = ['kube-system', 'default', 'istio', 'istio-system']
        pods = [p for p in pods.items if p.metadata.namespace in ns_list]

        rest = []
        for pod in pods:
            mypod = {}
            mypod['container'] = []


            # mypod['duty'] = 'hjw'
            mypod['name'] = pod.metadata.name
            mypod['namespace'] = pod.metadata.namespace
            mypod['pod_phase'] = pod.status.phase
            mypod['node_ip'] = pod.status.host_ip
            mypod['is_solved'] = "待处理"
            mypod['is_issue'] = False
            mypod['comment'] = ''
            mypod['check_time'] = time1


            issue_flag = False

            container_statuses = pod.status.container_statuses
            if container_statuses:
                for container_status in container_statuses:
                    mycontainer = {}
                    mycontainer['name'] = container_status.name
                    mycontainer['restart_count'] = container_status.restart_count
                    mycontainer['ready'] = container_status.ready
                    # mycontainer['state'] = container_status.state
                    tmp = container_status.state
                    if tmp.waiting:
                        mycontainer['state'] = tmp.waiting.reason
                        issue_flag = True

                    elif tmp.terminated and tmp.terminated.exit_code != 0:
                        mycontainer['state'] = tmp.terminated.reason
                        issue_flag = True

                    else:
                        rest.append(mypod)

                    mypod['container'].append(mycontainer)


            if issue_flag:
                mypod['is_issue'] = True
                self.pods_info.append(mypod)

        top_n = 5
        # 如果 凑不齐 top 5,最后几个pod 会重复 mongo_insert_many 可能会出插入重复的问题。
        restart_most = sorted(rest, key=lambda x: x['container'][0]['restart_count'], reverse=True)[:top_n]
        # print(rest)
        # restart_most = sorted(rest, key=[q['container'[0]['restart_count']] for q in rest], reverse=True)[:top_n]
        # time.sleep(100)
        new_restart = []
        name = ''
        for i in restart_most:
            if name == i['name']:
                break
            else:
                name = i['name']
                new_restart.append(i)

        self.pods_info.extend(new_restart)

        for pod in self.pods_info:
            pod['env_name'] = self.env_name
            pod['env_ip'] = self.env_ip
            pod['cluster_name'] = self.cluster_name
            pod['cluster_ip'] = self.cluster_ip
            pod['uuid'] = str(uuid.uuid4())

            if self.is_manul:
                pod['check_time'] = pod['check_time'].replace('2020', '2019')
                pod['fake'] = True
            if 'clever' in pod['env_name']:
                pod['duty'] = '史缙美'
            else:
                pod['duty'] = get_duty_man(pod['name'])

        self.db.pod.insert_many(self.pods_info)


def check_cluster(is_manul=False):
    print("开始了" + str(datetime.now()))
    get_cluster()
    MYDB = get_db()
    cur = MYDB.cluster.find({})
    cluster = cur[0]['data']        # 没有怎么办

    for i in cluster:
        with open('tmp.cfg','w') as f:
            f.write(i['cfg'])
        config.kube_config.load_kube_config('tmp.cfg')

        a = ClusterInspect(i['env_name'], i['env_vip'], i['alias'] ,i['cluster_ip'], is_manul=is_manul)

        # a.get_nodes_info()
        a.get_pods_info()

    # get_today_duty_list()


if __name__ == '__main__':
    # check_cluster(is_manul=False)
    check_cluster(is_manul=True)