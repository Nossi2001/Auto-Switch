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

        # 1. Tworzenie interfejsu VLAN na eth1 z adresem IP i opisem
        vlan_id = 100
        parent_interface = 'eth1'
        vlan_address = '192.168.100.1/24'
        vlan_description = 'Interfejs VLAN 100'

        if router.create_vlan_interface(parent_interface, vlan_id, address=vlan_address, description=vlan_description):
            print(f"Utworzono interfejs VLAN {vlan_id} na {parent_interface}.")

        # 2. Konfiguracja interfejsu eth2 jako portu dostępu dla VLAN 100
        access_interface = 'eth2'
        if router.configure_access_port(access_interface, vlan_id):
            print(f"Skonfigurowano {access_interface} jako port dostępu dla VLAN {vlan_id}.")

        # 3. Konfiguracja interfejsu eth3 jako portu trunk dla VLAN-ów 100, 200, 300
        trunk_interface = 'eth3'
        allowed_vlans = [100, 200, 300]
        if router.configure_trunk_port(trunk_interface, allowed_vlans):
            print(f"Skonfigurowano {trunk_interface} jako port trunk dla VLAN-ów {', '.join(map(str, allowed_vlans))}.")

        # 4. (Opcjonalnie) Usuwanie interfejsu VLAN
        # if router.delete_vlan_interface(parent_interface, vlan_id):
        #     print(f"Usunięto interfejs VLAN {vlan_id} z {parent_interface}.")

        # Rozłączenie z routerem
        router.disconnect()
        print("Rozłączono z routerem.")
    else:
        print("Nie udało się połączyć z routerem.")
