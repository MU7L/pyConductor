from PySide6.QtCore import QThread
from PySide6.QtWidgets import QApplication

from jobs.analyzer import Analyzer
from jobs.collector import Collector
from jobs.machine import Machine
from jobs.recognizer import Recognizer

from utils.config import ConfigCenter
from worker.signals import Signals


class Worker(QThread):

    def __init__(self, parent: QApplication, signals: Signals, config: ConfigCenter):
        super().__init__(parent)

        # 构建任务
        collector_job = Collector(config)
        recognizer_job = Recognizer(config)
        analyzer_job = Analyzer(config)
        machine_job = Machine(config, signals)

        # 构建任务链
        collector_job.connect(recognizer_job)
        recognizer_job.connect(analyzer_job)
        analyzer_job.connect(machine_job)

        self.jobs = [collector_job, recognizer_job, analyzer_job, machine_job]

    def run(self):
        for job in self.jobs:
            job.start()
        self.jobs[0].read()  # 阻塞
        for job in self.jobs:
            job.stop()
