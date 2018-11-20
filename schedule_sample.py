#  inspired by https://adamj.eu/tech/2014/08/16/time-to-move-on-from-cron/
# to keep things running, on a separate thread, try http://supervisord.org/
import schedule
import time
from twilio_sample import send_message
import logging


message = 'Hey this is a test'


def log_job(job_func, *args):
    logger.info("Running `{}`".format(job_func.__name__))
    job_func(*args)

# schedule.every().day.at('21:00').do(log_job, job)
schedule.every(.1).minutes.do(log_job, send_message, message)

def main():  
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)s - %(message)s')
    logger.setLevel(logging.INFO)
    main()