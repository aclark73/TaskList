from sqlalchemy import create_engine
from sqlalchemy.types import DateTime
# engine = create_engine('sqlite:///:memory:', echo=True)
from socket import gethostname
import os

FILE_ROOT = os.path.expanduser('~/.TaskList')
if not os.path.exists(FILE_ROOT):
    os.makedirs(FILE_ROOT)
DB_URL = 'sqlite:///%s/tasks.db' % FILE_ROOT

# if 'honu' in gethostname():
#     DB_URL = 'sqlite:////workspace/test/TaskList/tasks.db'
# else:
#     DB_URL = 'sqlite:////tmp/tasks.db'

engine = create_engine(DB_URL, echo=True)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

# class Project(Base):
#     __tablename__ = 'projects'
# 
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
# 
#     def __repr__(self):
#        return "<Project(name='%s')>" % (
#                             self.name,)

class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    project = Column(String)
    name = Column(String)
    source = Column(String)
    issue_id = Column(String)

    def __repr__(self):
        return "<Task(project='%s', name='%s')>" % (
                            self.project, self.name)

    def __str__(self):
        s = [self.project]
        if self.name:
            s.append(self.name)
        return " | ".join(s)

    @classmethod
    def get_or_create(cls, **attrs):
        task = session.query(Task).filter_by(**attrs).first()
        if not task:
            task = Task(**attrs)
            session.add(task)
            session.commit()
        return task
    
    @classmethod
    def query(cls):
        return session.query(Task)

NO_TASK = Task(name="None")

class TaskLog(Base):
    __tablename__ = 'task_log'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(ForeignKey('task.id'))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    
    task = relationship("Task", backref=backref('logs', order_by=id))
    
    def __repr__(self):
        return "<TaskLog(task='%s', start_time='%s', end_time='%s')>" % (
            self.task, self.start_time, self.end_time)

    @classmethod
    def log(cls, task, start_time, end_time):
        log = TaskLog(task=task, start_time=start_time, end_time=end_time)
        session.add(log)
        session.commit()
        return log

    @classmethod
    def query(cls):
        return session.query(TaskLog)

_verified_db = False
def verify_db():
    if not _verified_db:
        try:
            for cls in (Task, TaskLog,):
                cls.query().count()
        except:
            Base.metadata.create_all(engine)

def run():
    verify_db()

if __name__ == '__main__':
    run()

