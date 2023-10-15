import requests
from abc import ABC,abstractmethod

class ecommerceBase(ABC):
    @abstractmethod 
    def getID(self):
        pass
    @abstractmethod
    def getPRODUCT(self):
        pass
    @abstractmethod
    def run(self):
        pass