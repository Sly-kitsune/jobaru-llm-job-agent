from abc import ABC, abstractmethod

class JobPlatform(ABC):
    def __init__(self, browser, config):
        self.browser = browser
        self.config = config

    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def search_jobs(self, query):
        pass

    @abstractmethod
    def apply_to_job(self, job_url):
        pass
