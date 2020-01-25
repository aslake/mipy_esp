from scheduler_light import Scheduler, Job
import time
import machine


def job1():
    print("jobb 1")


def job2():
    print("jobb 2")


schedule = Scheduler("Test program",
                     Job("Job 1", job1, 2, 3),
                     Job("Job 2", job2, 4, 3))


while len(schedule.jobs) > 0:
    ind = schedule.follow_up_jobs()
    time.sleep(0.25)


# Test av next_time metoden
j3 = Job("Job 3", job1, 5, 5)
now = machine.RTC().datetime()
print("now = ", now)
now_sec = time.time()
yyyy, mm, dd, wday, hh, mm, sec, ms = now
mm += 1
j3.set_next_run(mm=mm)

schedule.add_jobs(j3)
while len(schedule.jobs) > 0:
    ind = schedule.follow_up_jobs()
    time.sleep(0.25)
