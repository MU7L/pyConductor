from typing import List

from utils.config import ConfigCenter, Observer


class Job(Observer):
    """管道过滤器模式构件"""

    def __init__(self, config: ConfigCenter):
        super().__init__(config)
        self.is_running: bool = False
        self.next_jobs: List[Job] = []

    def connect(self, next_job: 'Job'):
        """连接下一个任务"""
        self.next_jobs.append(next_job)

    def start(self):
        """启动"""
        self.is_running = True

    def read(self, *args, **kwargs):
        """读取上个任务的输出，由上个任务调用，一般不重写"""
        self.process(*args, **kwargs)

    def process(self, *args, **kwargs):
        """数据处理，由子类重写"""
        self.write(*args, **kwargs)

    def write(self, *args, **kwargs):
        """输出当前任务结果，调用下个任务，一般不重写"""
        for job in self.next_jobs:
            if job.is_running:
                job.read(*args, **kwargs)

    def stop(self):
        """终止"""
        self.is_running = False
