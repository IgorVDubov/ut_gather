import schedule
import time


def job():
    print("I'm working...")


# Run job every 3 second/minute/hour/day/week,
# Starting 3 second/minute/hour/day/week from now
schedule.every(3).seconds.do(job)
# schedule.every(3).minutes.do(job)
# schedule.every(3).hours.do(job)
# schedule.every(3).days.do(job)
# schedule.every(3).weeks.do(job)


while True:
    schedule.run_pending()
    time.sleep(1)
