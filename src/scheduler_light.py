"""Job scheduler - light version.

Inspiration: https://github.com/rguillon/schedule

Torbjørn Pettersen, 12.01.2020.
"""
import utime
import machine
import utime
import config
import logfile

log = logfile.LogFile("scheduler", "scheduler.log", config.log_sizelimit,
                      config.log_level, config.log_print)


class Job:
    """Job class.

    :param name: job name
    :type name: str
    :param job: function called to do job
    :type job: fun
    :param repeat: number of times to repeat job
    :type repeat: int
    :param interval: number of seconds between repeated job runs
    :type interval: int
    :returns: Job object to be used by Scheduler
    :rtype: object
    """

    def __init__(self, name, job, interval, repeat):
        self.name = name          # string
        self.job = job            # function to be evaluated
        self.interval = interval  # seconds
        self.repeat = repeat      # number of times to repeat
        self.repeated = 0
        self.next_run = utime.time() + int(interval)  # time for next run

    def set_next_run(self, **kwargs):
        """Set next time Job should run.

        :param yyyy, mmm, dd: optional year, month, day
        :type yyyy, mmm, dd: int
        :param hh, mm: optional hour and minutes
        :type hh, mm: int

        Usage:
        -----
        Next run today at 23:59: job.set_next_run(hh=23, mm=59)
        Next run April 3rd @ current time: job.set_next_run(mmm=4, dd=3)
        """
        now = machine.RTC().datetime()
        yyyy, mmm, dd, wday, hh, mm, sec, ms = now
        yyyy = kwargs.get("yyyy", int(yyyy))
        mmm = kwargs.get("mmm", int(mmm))
        dd = kwargs.get("dd", int(dd))
        hh = kwargs.get("hh", int(hh))
        mm = kwargs.get("mm", int(mm))
        future = (yyyy, mmm, dd, wday, hh, mm, sec, ms)
        log.debug("Set next_run to: %s" % str(future))
        machine.RTC().datetime(future)
        self.next_run = utime.time()
        machine.RTC().datetime(now)

    def run(self):
        now = utime.time()
        if now < self.next_run:
            return False

        if self.repeat == -1:  # repeat = -1 => Run forever..
            self.job()
            self.repeated += 1
            self.next_run = now + int(self.interval)
            return True

        elif self.repeated >= self.repeat:
            log.info("Skipped job %s, repeated %s times." % (
                self.name, self.repeated))
            return -1

        else:
            self.job()
            self.repeated += 1
            self.next_run = now + int(self.interval)
            return True


class Scheduler:
    """Job scheduler"""

    def __init__(self, name, *args):
        self.name = name
        self.jobs = [job for job in args]

    def follow_up_jobs(self):
        """Check if jobs are due to execute"""
        for i, job in enumerate(self.jobs):
            status = job.run()
            if status == -1:  # Job has been repeated enough.
                log.info("Job %s completed and removed from job list." %
                         (job.name))
                if i == 0:
                    self.jobs = self.jobs[1:]
                else:
                    self.jobs = self.jobs[:i-1] + self.jobs[i:]
            else:
                if status:
                    log.debug("Job %s executed." % (job.name))
            if len(self.jobs) == 0:
                log.debug("Scheduler %s has no jobs." % (self.name))

    def add_jobs(self, *args):
        """Add jobs to list of jobs."""
        self.jobs += [job for job in args]
