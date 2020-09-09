from pymongo import MongoClient

URL = '192.168.131.29'
# URL = 'localhost'


def get_db():
    client = MongoClient(f'mongodb://mongoadmin:mongoadmin@{URL}:27017/cluster_check?authSource=admin')
    db = client['cluster_check']
    return db

def delete():
    db = get_db()
    db['pod'].delete_many({})
    db['node'].delete_many({})


if __name__ == '__main__':
    # test()
    # delete()
    pass