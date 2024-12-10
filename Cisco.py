def delete_configuration(ports):
    var = '''enable
configure terminal
'''
    for port in ports:
        var += f'default interface {port}\n'
    var += '''exit
'''
    return var


def disable_ports(ports):
    config = '''enable
configure terminal
'''
    for port in ports:
        config += f'''interface {port}
shutdown
exit
'''
    config += '''exit
write memory
'''
    return config


ports = ["FastEthernet0/0"]
config = delete_configuration(ports)
print(config)
