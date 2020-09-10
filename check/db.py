from pymongo import MongoClient


URL = '192.168.131.29'
# URL = 'localhost'


def get_db():
    client = MongoClient(f'mongodb://mongoadmin:mongoadmin@{URL}:27017/cluster_check?authSource=admin')
    db = client['cluster_check']
    return db


def delete_all():
    db = get_db()
    # db.node.delete_many({})
    # db.cluster.delete_many({})
    # db.node.delete_many({})
    # db.pod.delete_many({})
    # db.pod.delete_many({'check_time': '2020-09-09'})
    db.pod.delete_many({'type': 'fake'})
    pass



if __name__ == '__main__':
    delete_all()
    pass