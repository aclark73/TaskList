from models import Task

class BaseSource():
    source = None
    
    def fetch(self):
        raise NotImplementedError
    
    def get_or_create_task(self, **task_kwargs):
        assert('source' in task_kwargs)
        assert('project' in task_kwargs or 'title' in task_kwargs)
        (task, created) = Task.get_or_create(**task_kwargs)
        if created:
            print "Created new task %s" % str(task)
        return task
