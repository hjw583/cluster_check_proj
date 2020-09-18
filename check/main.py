import time
from apscheduler.schedulers.background import BlockingScheduler
from collect_info import check_cluster
from get_data import get_msg
from datetime import datetime


def tester(is_manul=False):
    print(is_manul)
    print(datetime.now())


def cron9():
    print(datetime.now())
    check_cluster(True)
    get_msg(True)
    time.sleep(3600)
    print(datetime.now())
    check_cluster()
    get_msg()
    # check_cluster(True)
    # get_msg(True)
    # scheduler.add_job(check_cluster, "cron", day="*", hour="00", minute='01', args=[True])
    # scheduler.add_job(get_msg, "cron", day='*', hour='00', minute='05', args=[True])

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    # cron9()
    scheduler.add_job(cron9, "cron", day="*", hour="00", minute='05')
    scheduler.start()

