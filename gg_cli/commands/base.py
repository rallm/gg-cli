from abc import ABC, abstractmethod
import argparse

class BaseCommand(ABC):
    def __init__(self, parser: argparse.ArgumentParser):
        self.parser = parser
        self.setup_args()

    @abstractmethod
    def setup_args(self) -> None:
        pass

    @abstractmethod
    def execute(self, args: argparse.Namespace) -> None:
        pass