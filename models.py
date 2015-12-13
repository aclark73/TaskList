from PyQt4 import QtCore
from socket import gethostname
from logging import getLogger
import os
import json
import requests
import sqlite3
import peewee
import datetime

LOGGER = getLogger(__name__)

ROOT = '/tmp/'
DB_FILE = ROOT + '.tasklist.db'

FILE_ROOT = os.path.expanduser('~/.TaskList')
if not os.path.exists(FILE_ROOT):
    os.makedirs(FILE_ROOT)
db = peewee.SqliteDatabase('%s/tasks.db' % FILE_ROOT)


# class Project(Base):
#     __tablename__ = 'projects'
# 
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
# 
#     def __repr__(self):
#        return "<Project(name='%s')>" % (
#                             self.name,)

class Task(peewee.Model):
    id = peewee.PrimaryKeyField()
    project = peewee.CharField()
    title = peewee.CharField()
    source = peewee.CharField()
    issue_id = peewee.CharField()

    class Meta:
        database = db

    def is_project(self):
        return not self.title

    def get_uid(self):
        if self.is_project():
            return "P.%s" % self.project
        elif self.issue_id:
            return "T.%s.%s" % (self.source, self.issue_id)
        else:
            return "T.%s.%s.%s" % (self.source, self.project, self.title)

    def get_label(self):
        s = []
        if self.issue_id:
            s.append("#%s" % self.issue_id)
        if self.title:
            s.append(str(self.title))
        elif self.project:
            s.append(str(self.project))
        return " ".join(s)

    def __repr__(self):
        return "<Task(project='%s', title='%s')>" % (
                            self.project, self.title)

    def __str__(self):
        s = []
        if self.issue_id:
            s.append("#%s" % self.issue_id)
        s.append(str(self.project))
        if self.title:
            s.append(self.title)
        return " | ".join(s)

Task.create_table(True)

NO_TASK = Task(title="None")

class TaskLog(peewee.Model):
    id = peewee.PrimaryKeyField()
    task = peewee.ForeignKeyField(Task)
    start_time = peewee.DateTimeField()
    end_time = peewee.DateTimeField()
    uploaded = peewee.BooleanField(default=False)
    
    class Meta:
        database = db

    # task = relationship("Task", backref=backref('logs', order_by=id))
    
    def __repr__(self):
        return "<TaskLog(task='%s', start_time='%s', end_time='%s')>" % (
            self.task, self.start_time, self.end_time)

    @classmethod
    def log(cls, task, start_time, end_time):
        log = TaskLog.create(task=task, start_time=start_time, end_time=end_time)
        return log

    @classmethod
    def query(cls):
        return session.query(TaskLog)

TaskLog.create_table(True)

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

UPLOADER = RedmineUploader()

if __name__ == '__main__':
    # run()
    UPLOADER.upload()

