from models import Task
from task_source.base import BaseSource

class LocalSource(BaseSource):
    source = 'local'
    
    def fetch(self):
        tasks = Task.select().where(Task.source==self.source, Task.title != '')
        for task in tasks:
            yield task

    def add(self, title, project=None):
        return self.get_or_create_task(
            source=self.source,
            project=project or '',
            title=title
        )
        
