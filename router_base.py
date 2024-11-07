# router_base.py
from abc import ABC, abstractmethod
import paramiko

class RouterBase(ABC):
    def __init__(self, ip, username, password, port=22):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.client = None  # Obiekt SSHClient

    def connect(self):
        try:
            print(f"Łączenie z urządzeniem {self.ip}...")
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                hostname=self.ip,
                port=self.port,
                username=self.username,
                password=self.password,
                look_for_keys=False,
                allow_agent=False
            )
            print("Połączono z urządzeniem.")
            return True
        except Exception as e:
            print(f"Wystąpił błąd podczas łączenia: {e}")
            return False

    def disconnect(self):
        if self.client is not None:
            self.client.close()
            self.client = None
            print("Rozłączono z urządzeniem.")

    @abstractmethod
    def change_ip(self, new_ip):
        pass  # Metoda abstrakcyjna, musi być zaimplementowana w klasach potomnych
