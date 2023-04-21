"""
Schedules tasks to run at particular times

Modules:

    3rd Party: apscheduler, yaml, importlib
    Internal: config

Classes:

    TBA

Functions

    sched_tasks()
        Schedule tasks

Exceptions:

    None

Misc Variables:

    LOCATION : str
        The location of the tasks config file

Author:
    Luke Robertson - April 2023
"""

from apscheduler.triggers.cron import CronTrigger
import yaml
import importlib

from config import PLUGINS


LOCATION = 'core\\tasks.yaml'


def sched_tasks(scheduler):
    '''
    Gets a list of tasks to schedule, and schedules them

    Parameters:
        scheduler : APScheduler class
            A globally defined APScheduler class

    Raises:
        Exception
            If the confif file couldn't be loaded

    Returns:
        None
    '''

    # Read the YAML file
    tasks = {}
    with open(LOCATION) as config:
        try:
            tasks = yaml.load(config, Loader=yaml.FullLoader)

        # Handle problems with YAML syntax
        except yaml.YAMLError as err:
            print('Error parsing config file, exiting')
            print('Check the YAML formatting at \
                https://yaml-online-parser.appspot.com/')
            print(err)
            return False

    # Each task gets its own scheduler
    for task in tasks:
        # The module needs to be in the correct format to import
        #   eg, 'plugins.junos.jtac_logs'
        plugin = PLUGINS[tasks[task]['plugin']]['module']
        plugin = plugin.split(".")
        plugin = f"{plugin[0]}.{plugin[1]}.{tasks[task]['module']}"

        # Load the module and function
        module = importlib.import_module(plugin)
        function = getattr(module, tasks[task]['func'])

        # Collect arguments into a dictionary
        arguments = {}
        for arg in tasks[task]['args']:
            for key, value in arg.items():
                arguments[key] = value

        # Define the trigger (the scheduled time)
        trigger = CronTrigger(
            day_of_week=tasks[task]['day_of_week'],
            hour=tasks[task]['hour'],
            minute=tasks[task]['minute'],
            second=tasks[task]['second'])

        # Schedule the job
        scheduler.add_job(
            id=task,
            func=function,
            kwargs=arguments,
            trigger=trigger
        )
