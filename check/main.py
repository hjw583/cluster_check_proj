from collect_info import check_cluster
from apscheduler.schedulers.background import BlockingScheduler

# def tester():
#     from datetime import datetime
#     print(datetime.now())

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(check_cluster, "cron", day="*", hour="08")
    # scheduler.add_job(tester, "cron", day="*", hour="23", minute="58")
    scheduler.start()
    # check_cluster()

