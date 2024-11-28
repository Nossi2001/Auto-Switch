# test_edge_router_vlan.py

from edge_router import EdgeRouter

if __name__ == "__main__":
    # Dane routera
    ip = '192.168.55.50'        # Aktualny adres IP routera
    username = 'user'           # Nazwa użytkownika
    password = 'user'           # Hasło do routera

    # Tworzenie instancji EdgeRouter
    router = EdgeRouter(ip=ip, username=username, password=password)

    # Nawiązywanie połączenia z routerem
    if router.connect():
        print("Połączono z routerem.")

    else:
        print("Nie udało się połączyć z routerem.")
