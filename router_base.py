# router_base.py

from abc import ABC, abstractmethod

class RouterBase(ABC):
    """
    Abstrakcyjna klasa bazowa dla routerów.
    Definiuje interfejs, który muszą implementować wszystkie klasy routerów.
    """

    def __init__(self, ip, username, password, port=22):
        """
        Inicjalizuje router z parametrami połączenia.
        """
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.client = None  # Obiekt klienta SSH lub innego protokołu

    @abstractmethod
    def connect(self):
        """
        Nawiązuje połączenie z routerem.
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Zamyka połączenie z routerem.
        """
        pass

    @abstractmethod
    def change_ip(self, interface_name, new_ip, netmask):
        """
        Zmienia adres IP na podanym interfejsie.
        """
        pass

    @abstractmethod
    def change_dns(self, new_dns):
        """
        Zmienia ustawienia DNS routera.
        """
        pass

    @abstractmethod
    def change_gateway(self, new_gateway):
        """
        Zmienia bramę domyślną routera.
        """
        pass

    @abstractmethod
    def disable_dhcp(self):
        """
        Wyłącza serwer DHCP na routerze.
        """
        pass
