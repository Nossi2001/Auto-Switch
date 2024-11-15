# test_openwrt_router.py

from open_wrt_router import OpenWrtRouter

if __name__ == "__main__":
    # Dane routera
    ip = '192.168.55.51'      # Początkowy adres IP routera
    username = 'root'         # Nazwa użytkownika
    password = 'Wadessa43#' # Hasło do routera

    router = OpenWrtRouter(ip=ip, username=username, password=password)
    # Nawiązywanie połączenia z routerem
    if router.connect():
        print("Połączono z routerem.")

        # Wyświetlenie aktualnych ustawień sieciowych
        print(f"Aktualny adres IP: {router.current_ip}")
        print(f"Aktualna maska podsieci: {router.current_netmask}")
        print(f"Aktualna brama domyślna: {router.current_gateway}")

        # Wykonanie kopii zapasowej
        if router.backup_configuration():
            print("Kopia zapasowa została wykonana.")
        else:
            print("Nie udało się wykonać kopii zapasowej.")

        # Ustawienie nowej nazwy hosta
        new_hostname = 'NowyHost'
        if router.set_hostname(new_hostname):
            print(f"Nazwa hosta została zmieniona na: {new_hostname}")
        else:
            print("Nie udało się zmienić nazwy hosta.")

        # Ustawienie nowej domeny
        new_domain = 'domena.lokalna'
        if router.set_domain(new_domain):
            print(f"Domena została zmieniona na: {new_domain}")
        else:
            print("Nie udało się zmienić domeny.")

        # Konfiguracja interfejsu 'lan' z nowym adresem IP
        new_ip = '192.168.55.51'    # Nowy adres IP dla interfejsu LAN
        netmask = '255.255.255.0'
        description = 'Interfejs LAN'
        enabled = True

        if router.configure_interface(
            interface_name=router.LAN_INTERFACE,
            ip_address=new_ip,
            netmask=netmask,
            description=description,
            enabled=enabled
        ):
            print(f"Interfejs {router.LAN_INTERFACE} został skonfigurowany.")
        else:
            print(f"Nie udało się skonfigurować interfejsu {router.LAN_INTERFACE}.")

        # Po ponownym połączeniu możemy wykonać dalsze operacje
        # Na przykład wyświetlić aktualne ustawienia
        print(f"Nowy adres IP: {router.current_ip}")
        print(f"Nowa maska podsieci: {router.current_netmask}")

        # Przykład tworzenia VLAN-u
        vlan_id = 10
        vlan_name = "VLAN10"
        if router.create_vlan(vlan_id, vlan_name):
            print(f"VLAN {vlan_id} został utworzony.")
        else:
            print(f"Nie udało się utworzyć VLAN {vlan_id}.")

        # Przypisywanie VLAN-u do interfejsu
        interface_name = 'lan'  # Używamy istniejącego interfejsu 'lan'
        if router.assign_vlan_to_interface(vlan_id, interface_name, tagged=True):
            print(f"VLAN {vlan_id} został przypisany do interfejsu {interface_name} jako tagowany.")
        else:
            print(f"Nie udało się przypisać VLAN {vlan_id} do interfejsu {interface_name}.")

        # Konfiguracja trunkingu na interfejsie
        trunk_interface = 'lan'  # Używamy istniejącego interfejsu 'lan'
        vlan_ids = [10, 20, 30]
        if router.configure_trunk(trunk_interface, vlan_ids):
            print(f"Interfejs {trunk_interface} został skonfigurowany jako trunk dla VLAN-ów {vlan_ids}.")
        else:
            print(f"Nie udało się skonfigurować trunkingu na interfejsie {trunk_interface}.")

        # Rozłączenie z routerem
        router.disconnect()
    else:
        print("Nie udało się połączyć z routerem.")
