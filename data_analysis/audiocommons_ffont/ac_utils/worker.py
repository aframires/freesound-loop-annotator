from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError, ProcessPoolExecutor
import time
import pymtg
# Docs: https://docs.python.org/3/library/concurrent.futures.html


class WorkParallelizer(object):
    """
    TODO: proper document that
    wp = WorkParallelizer()
    for i in range(30):
        wp.add_task(my_function, i, i + 1, kwarg1='one', kwarg2='two')
    wp.run()
    if wp.num_tasks_failed > 0:
        print('\nErrors:')
        wp.show_errors()
    """
    
    def __init__(self, show_widgets=True, use_threads=False):
        """
        """
        self.tasks = []
        self.futures = []
        self.executor = None
        self.starttime = None
        self.progress_widget = None
        self.show_widgets = show_widgets
        if use_threads:
            self.pool_executor=ThreadPoolExecutor
        else:
            self.pool_executor=ProcessPoolExecutor
        
    def add_task(self, fn, *args, **kwargs):
        '''
        Use special kwarg task_id to specify an id for the task. Otherwise will use a count number.
        '''
        if self.has_started_computing:
            print('Can\'t add new tasks once computing has started.')
            return False
        
        if 'task_id' in kwargs:
            tid = kwargs['task_id']
            del kwargs['task_id']
        else:
            tid = len(self.tasks)
            
        self.tasks.append((fn, args, kwargs, tid))
        return True
        
    def tasks_running(self):
        """
        Return a list of `future` objects corresponding to all tasks that are
        currently being processed.
        """
        return [future for future in self.futures if future.running()]

    def tasks_completed(self):
        """
        Return a list of `future` objects corresponding to all tasks that have
        completed processing, including those that failed.
        """
        return [future for future in self.futures if future.done()]
    
    def tasks_failed(self):
        """
        Returns a list of `future` objects corresponding to all tasks that have
        raised an exception (i.e. that have failed).
        """
        to_return = []
        for future in self.futures:
            try:
                if future.exception(timeout=0.0) is not None:
                    to_return.append(future)
            except TimeoutError:
                # concurrent.futures.TimeoutError, meaning that task has not been finished (or has not started)
                pass 
        return to_return
    
    def tasks_succeeded(self):
        """
        Returns a list of `future` objects corresponding to all tasks that have been
        completed successfully. Tasks are considered to have finished successfully
        as long as no exceptions happened during their computation.
        Given a `future` object, the corresponding task result can be retrieved as `future.result()`
        Given a `future` object, you can get its given id by using `future.id`
        """
        to_return = []
        for future in self.futures:
            try:
                future.result(timeout=0.0)  # If task has not been successful, this will raise an Exception
                to_return.append(future)
            except TimeoutError:
                # concurrent.futures.TimeoutError, meaning that task has not been finished (or has not started)
                pass
            except Exception:
                # Intentionally catch broad exception here as it could be any exception triggered by the function
                pass
        return to_return
    
    @property
    def num_tasks(self):
        return len(self.tasks)

    @property
    def num_tasks_completed(self):
        return len(self.tasks_completed())
    
    @property
    def num_tasks_running(self):
        return len(self.tasks_running())
    
    @property
    def num_tasks_failed(self):
        return len(self.tasks_failed())
    
    @property
    def num_tasks_succeeded(self):
        return len(self.tasks_succeeded())
    
    @property
    def has_started_computing(self):
        return len(self.futures) > 0
       
    def start(self, num_workers=4):
        """
        Starts the computation of the tasts. Returns False if computation couldn't start.
        Calling this method does not block the main thread.
        """
        if self.has_started_computing:
            print('Computing has already started, can\'t start again.')
            return False
        
        print('Submitting {0} tasks to {1} workers'.format(self.num_tasks, num_workers))
        self.tasks_succeeded_cache = []
        self.executor = self.pool_executor(max_workers=num_workers)
        self.start_time = time.time()
        for (fn, args, kwargs, tid) in self.tasks:
            future = self.executor.submit(fn, *args, **kwargs)
            future.id = tid
            future.command = '{0}({1}{2})'.format(
                fn.__name__,
                ', '.join([str(arg) for arg in args]) if args else '',
                ', ' + ', '.join(['{0}={1}'.format(str(key), str(value)) for key, value in kwargs.items()]) if kwargs else ''
            )
            self.futures.append(future)     
        return True
            
    def show_progress(self, in_blocking_loop=False):
        """
        Get number of completed tasks and compute estimated remaining time. Display that information
        on screen. Uses FloatProgress widget if available.
        Returns true if computation of all tasks has fininshed.
        """
        num_tasks_completed = self.num_tasks_completed  # Do this here to iterate over the futures only once
        
        if num_tasks_completed > 0:
            _, remaining_time = pymtg.time.time_stats(num_tasks_completed, self.num_tasks, self.start_time)
            remaining_time += ' remaining'
        else:
            remaining_time = '-'
   
        if self.show_widgets:
            try:
                from ipywidgets import FloatProgress
                from IPython.display import display
                use_widgets = True
            except ImportError:
                use_widgets = False
        else:
            use_widgets = False

        if use_widgets:
            if self.progress_widget is None or not in_blocking_loop:
                self.progress_widget = FloatProgress(min=0, max=self.num_tasks)
                display(self.progress_widget)
            self.progress_widget.value = num_tasks_completed
            
        print('\r[{0}/{1}, {2} running] {3}'.format(
            num_tasks_completed, self.num_tasks, self.num_tasks_running, remaining_time
        ), end='')
            
        if num_tasks_completed == self.num_tasks:  # All tasks have been completed
            return True
            print('\rAll tasks compelted! [{0} succeeded, {1} failed]'.format(
                self.num_tasks_succeeded, self.num_tasks_failed))
        return False
       
    def show_progress_blocking(self, interval_seconds=0.2):
        """
        Check the progreess of the computation every `interval_seconds` and display it 
        on screen.
        """
        if not self.has_started_computing:
            print('Computinng has not started yet, can\'t show progress.')
            return
        
        while True:
            time.sleep(interval_seconds)
            finished = self.show_progress(in_blocking_loop=True)
            if finished:
                break
                
    def show_errors(self):
        """
        Displays on screen information about the tasks that failed, including the command
        that was run and the exception that was raised.
        """
        for task in self.tasks_failed():
            print('* Task {0}\nCommand: {1}\nException: {2}\n'.format(
                task.id, 
                task.command,
                task.exception()
            ))
                
    def run(self, num_workers=4):
        """
        Runs all the tasks that have been added to WorkParallelizer and shows the overall
        progress in periodic updates. This method blocks the main thread.
        """
        started = self.start(num_workers=num_workers)
        if started:
            self.show_progress_blocking()