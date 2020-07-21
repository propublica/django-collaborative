import os

from apscheduler.schedulers.blocking import BlockingScheduler


sched = BlockingScheduler({
    'apscheduler.executors.default': {
        'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
        'max_workers': '1'
    },
    'apscheduler.job_defaults.coalesce': 'false',
    'apscheduler.job_defaults.max_instances': '1',
    'apscheduler.timezone': 'UTC'
})


@sched.scheduled_job('interval', minutes=15)
def refresh_data_sources():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collaborative.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    argv = ['./manage.py', 'refresh_data_sources']
    execute_from_command_line(argv)


sched.start()
