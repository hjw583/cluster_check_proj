import base64

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

from mongo import get_db

db = get_db()
app = Flask(__name__)
CORS(app, support_credentials=True)  # Access-Control-Allow-Origin: *


def get_token():
    text = 'admin:Pwd123456'
    return "Basic " + base64.b64encode(text.encode()).decode()


headers = {
    'Content-Type': 'application/json',
    'Authorization': get_token()
}


@app.route('/', methods=['GET'])
def hello():
    return jsonify({'hello': 'hello1',
                    'msg': 'hahaha'}), 201

@app.route('/user/duty', methods=['GET', 'POST'])
def duty():
    info = {
        'success' : False
    }
    if request.method == 'POST':
        data = request.json.get('data')
        db.user.delete_many({})
        db.user.insert_many(data)
        # for i in data:
            # db.user

    elif request.method == 'GET':
        info['data'] = []
        cur = db.user.find({})
        for i in cur:  # 如果为空怎么办 db.env表什么都没有
            i.pop('_id')
            info['data'].append(i)
        info['success'] = True
        return jsonify(info)

    return info


@app.route('/env', methods=['GET', 'POST'])
def env():
    info = {'success': False, 'update_num': 0}
    if request.method == 'POST':
        data = request.json.get('data')  # upsert
        db.env.delete_many({})
        res = db.env.insert_many(data)
        info['update_num'] = len(res.inserted_ids)
        info['success'] = True

    elif request.method == 'GET':
        date = request.args.get('date')
        cur = db.env.find({'date':date})
        info['data'] = []
        for i in cur:  # 如果为空怎么办 db.env表什么都没有
            i.pop('_id')
            info['data'].append(i)

        info['success'] = True

    return jsonify(info)


@app.route('/cluster', methods=['GET', 'POST'])
def cluster():
    # date = request.args.get('date')
    if request.method == 'GET':
        date = request.args.get('date')

        '''
        这里得改代码逻辑，预先查一下数据库？如果为空，去compass取，否则直接返回数据库的数据。
        '''
        cur = db.env.find({'date': date})
        vip = cur[0]['vip']
        url = f'http://{vip}:6060/hodor/apis/admin.cluster.caicloud.io/v2alpha1/clusters'
        res = requests.get(url=url, headers=headers)
        cluster_list = res.json()['items']
        print(cluster_list)
        return cluster_list

    elif request.method == 'POST':
        data = request.json.get('data')  # upsert
        db.cluster.delete_many({})
        for i in data:
            db.cluster.insert_one(i)

            # info['update_num'] += 1
        # info['success'] = True
        pass

    # return jsonify(cluster_list)


@app.route('/node', methods=['GET'])
def get_node():
    """
    :return:
    """
    date = request.args.get('date')
    # env = request.args.get('env')
    # cluster_name = request.args.get('cluster_name')

    print(date)

    nodes = db.node.find(
                        {'check_time': date,
                          }
                         )  # 没有这个cluster 怎么办  需要做判断

    nodes_info = nodes[0]['nodes_info']
    not_ready = [i for i in nodes_info if i['condition'] != 'Ready']

    info = {
            'not_ready': not_ready,
            'node_healthy': False if not_ready else True}

    return jsonify(info)  # 会做压缩，如果使用自带库 content_type 会不一样

    # if not_ready:
    #     return {'node_healthy' : False, 'not_ready' : not_ready}, 200
    # else:
    #     return {'node_healthy' : True}, 201

@app.route('/single_pod', methods=['GET', 'POST'])  # date = '2020-08-29'
def single_pod():
    if request.method == 'GET':
        uuid4 = request.args.get('uuid')
        pass

    elif request.method == 'POST':
        data = request.json.get('data')
#        print(data)
        db.pod.update_one({'uuid': data['uuid']}, {'$set': {'is_solved': data['is_solved']}})

    pass
    return "hello"



@app.route('/pod', methods=['GET'])  # date = '2020-08-29'
def get_pod():
    import time
    # 当get请求时，需要使用request.args来获取数据
    # 当post请求时，需要使用request.form来获取数据

    date = request.args.get('date')

    cur = db.pod.find({'check_time': date})
    pods = []
    for i in cur:  # 如果为空怎么办 db.env表什么都没有
        i.pop('_id')
        pods.append(i)
    # for i in cur:
    #     pods.extend(i['pods_info'])

    return jsonify(pods)



# @app.route('/pod/restart_most', methods=['GET'])  # date = '2020-08-29'
# def get_pod_restart_most():
#     # 当get请求时，需要使用request.args来获取数据
#     # 当post请求时，需要使用request.form来获取数据
#
#     date = request.args.get('date')
#     cluster_name = request.args.get('cluster_name')
#
#     pods = db.pod.find({'check_time': date, 'cluster_name': cluster_name})  # 同样没有这个集群或时间怎么办
#
#     pods_info = pods[0]['pods_info']
#     sys_ns = ['kube-system', 'default']
#     rest = []
#     for pod in pods_info:
#         if pod['container'] and pod['namespace'] in sys_ns:
#             rest.append(pod)
#     top_n = 5
#     restart_most = sorted(rest, key=lambda x: x['container'][0]['restart_count'], reverse=True)[:top_n]
#
#     info = {'check_time': date, 'restart_most': restart_most}
#
#     # return jsonify(info)
#     return info


if __name__ == '__main__':
    app.run(debug=True)






