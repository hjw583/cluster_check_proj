import time
import os
import json
# import time
import uuid
from datetime import datetime
from kubernetes import client, config

from db import get_db
from get_data import get_duty, get_cluster

Duty = get_duty()


class ClusterInspect:
    def __init__(self,env_name, env_ip, cluster_name, cluster_ip):
        self.env_name = env_name
        self.env_ip = env_ip
        self.cluster_name = cluster_name
        self.cluster_ip = cluster_ip

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

        # self.all_info['nodes_info'] = self.nodes_info
        # self.nodes_info = {'check_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) }
        db_nodes_info = {
                         'env': self.env_ip,
                         'cluster_name': self.cluster_name,
                         'check_time': str(datetime.date(datetime.now())),          # 2020-09-01
                         'nodes_info': self.nodes_info
                        }

        self.db.node.insert_one(db_nodes_info)
        print('xx')


    def get_pods_info(self):
        time1 = str(datetime.date(datetime.now()))
        pods = self.v1.list_pod_for_all_namespaces()
        ns_list = ['kube-system', 'default', 'istio', 'istio-system']
        pods = [p for p in pods.items if p.metadata.namespace in ns_list]

        rest = []
        for pod in pods:
            mypod = {}
            container_statuses = pod.status.container_statuses
            mypod['container'] = []
            mypod['env_name'] = self.env_name
            mypod['env_ip'] = self.env_ip
            mypod['cluster_name'] = self.cluster_name
            mypod['cluster_ip'] = self.cluster_ip

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
                # mypod['uuid'] = str(uuid.uuid4())
                self.pods_info.append(mypod)

        top_n = 5

        restart_most = sorted(rest, key=lambda x: x['container'][0]['restart_count'], reverse=True)[:top_n]

        self.pods_info.extend(restart_most)

        for pod in self.pods_info:
            pod['uuid'] = str(uuid.uuid4())

            if 'clever' in pod['env_name']:
                pod['duty'] = '史缙美'
            else:
                pod['duty'] = get_duty_man(pod['name'])

        self.db.pod.insert_many(self.pods_info)

def check_cluster():
    get_cluster()
    mydb = get_db()
    cur = mydb.cluster.find({})
    cluster = cur[0]['data']
    for i in cluster:
        print(i)
        with open('tmp.cfg','w') as f:
            f.write(i['cfg'])
        config.kube_config.load_kube_config('tmp.cfg')
        # ...
        a = ClusterInspect(i['env_name'], i['env_vip'], i['alias'] ,i['cluster_ip'])
        a.get_nodes_info()
        a.get_pods_info()

#
# def check_env(env):
#     pass

    # 有问题   k8cfg/2.11-rc05/...
    # DIR = os.path.abspath(os.path.dirname(__file__))

    # for root, dirs, files in os.walk(f'k8cfg/{env}'):
        # cmd = f'rm -r daily_info/{env}'
        # os.system(cmd)
        # cmd = f'mkdir daily_info/{env}'
        # os.system(cmd)

        # for name in files:
        #     print(os.path.join(root, name))
        #     config.kube_config.load_kube_config(config_file=os.path.join(root, name))
        #     cname = name.split('.cfg')[0]  # 最后一个. 之前的
        #
        #     a = ClusterInspect(env, cname)
        #
        #     a.get_nodes_info()
        #     a.get_pods_info()

            # with open(f'{DIR}/daily_info/{env}/{cname}.json', 'w') as f:
            #     json.dump(a.all_info, f)



    # delete config
# import uuid
# def uuid1():
#     a = uuid.uuid4()
#     print(a)
#     print(type(a))

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


    pass


if __name__ == '__main__':
    # check_env('2.11-rc05')
    # pass
    # load_cfg('2.11-rc4')
    # load_cfg('rmrb-hz')
    # check_cluster()
    # uuid1()
    # print(Duty)
    # get_duty_man(pod_name='*')
    pass