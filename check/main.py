from apscheduler.schedulers.background import BlockingScheduler
from collect_info import check_cluster
from get_data import get_today_duty_list


def tester(is_manul=False):
    print(is_manul)
    from datetime import datetime
    print(datetime.now())

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(check_cluster, "cron", day="*", hour="00", minute='58')
    scheduler.add_job(get_today_duty_list, "cron", day='*', hour='01', minute='00')
    # scheduler.add_job(check_cluster, "cron", day="*", hour="23", minute='*/1', args=[True])
    # scheduler.add_job(get_today_duty_list, "cron", day='*', hour='23', minute='*/1', args=[True])


    # scheduler.add_job(tester, "cron", day="*", hour="23", second="*/2")
    # scheduler.add_job(tester, "cron", day="*", hour="23", second="*/7",args=[True])

    scheduler.start()

