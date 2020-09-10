from apscheduler.schedulers.background import BlockingScheduler
from collect_info import check_cluster


def tester():
    from datetime import datetime
    print(datetime.now())

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    # print("qqq")
    scheduler.add_job(check_cluster, "cron", day="*", hour="01")
    # check_cluster()
    # scheduler.add_job(send, "cron", args=["xxx"], day="*", hour="*", minute="*", second="*/30")

    # scheduler.add_job(check_cluster, "cron", day="*", hour="08", minute="00", second="00")
    # scheduler.add_job(tester, "cron", day="*", hour="21", minute="53", second="*/5")
    scheduler.start()
    # check_cluster()

