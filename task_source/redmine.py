from models import Task
from task_source.base import BaseSource
from socket import gethostname
import requests
import json


class RedmineSettings():
    if 'honu' in gethostname().lower():
        BASE_URL = 'http://dmscode.iris.washington.edu/'
    else:
        BASE_URL = 'http://localhost/'
    USER = 3
    ISSUES_URL =  '%s/issues.json?key=fb0ace80aa4ed5d8c113d5ecba70d6509b318837&assigned_to_id=me&sort=updated_on:desc&status_id=open&limit=200'
    ISSUE_URL =  '%s/issues/%s'


class RedmineSource(BaseSource):
    def fetch(self):
        if 'localhost' in RedmineSettings.BASE_URL:
            with open('redmine.json') as f:
                j = json.load(f)
        else:
            r = requests.get(RedmineSettings.ISSUES_URL % RedmineSettings.BASE_URL)
            if r.ok:
                j = r.json()
        for issue in j.get('issues'):
            yield self.get_or_create_redmine_task(issue)
    
    def get_or_create_redmine_task(self, issue):
        return self.get_or_create_task(
            source='redmine',
            issue_id=issue.get('id'),
            title=issue.get('subject'),
            project=issue.get('project', {}).get('name')
        )
    

REDMINE_TASK_URL = 'http://dmscode.iris.washington.edu/time_entries.json?key=fb0ace80aa4ed5d8c113d5ecba70d6509b318837'

class RedmineUploader():

    timer = None
    interval = 1000*60*60*8 # 8 hours
    
    def start(self):
        self.upload()
        if not self.timer:
            self.timer = QtCore.QTimer()
            self.timer.setInterval(self.interval)
            self.timer.timeout.connect(self.upload)
        if not self.timer.isActive():
            self.timer.start()
    
    def stop(self):
        if self.timer and self.timer.isActive():
            self.timer.stop()
    
    def upload(self):
        logs = peewee.SelectQuery(TaskLog).where(
            TaskLog.uploaded != True,
            TaskLog.end_time < datetime.date.today()
            ).join(Task)
        LOGGER.info("Found %d entries to upload" % len(logs))
        hours_per_issue_per_day = {}
        for log in logs:
            issue_id = log.task.issue_id
            if issue_id:
                time_spent = log.end_time - log.start_time
                day = log.start_time.date().isoformat()
                hours_per_issue_per_day.setdefault(day, {}).setdefault(issue_id, 0)
                hours_per_issue_per_day[day][issue_id] += float(time_spent.seconds) / 3600
        
        for day, issues in hours_per_issue_per_day.iteritems():
            for issue_id, hours in issues.iteritems():
                log_dict = dict(
                    time_entry=dict(
                        issue_id=int(issue_id),
                        spent_on=day,
                        hours=hours
                    )
                )
                requests.post(REDMINE_TASK_URL, json=log_dict)
                print json.dumps(log_dict)
    
        for log in logs:
            log.uploaded = True
            log.save()
