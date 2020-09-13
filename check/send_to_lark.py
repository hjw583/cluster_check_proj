import requests
import json


def send(msg):
    data = {
        'text': msg
    }

    headers = {'Content-Type': 'application/json'}
    # url = 'https://open.feishu.cn/open-apis/bot/hook/aa29477b-c85e-4391-8020-d64dfdd397a5'  # qa
    # url = 'https://open.feishu.cn/open-apis/bot/hook/996f08f1-da5f-4b24-8b52-10ccdcf04cba'
    url = 'https://open.feishu.cn/open-apis/bot/hook/0f582007-aecc-4dd9-9a6e-b579ad7bee02'
    response = requests.post(url=url, headers=headers, data=json.dumps(data))

if __name__ == '__main__':
    send('xx')
