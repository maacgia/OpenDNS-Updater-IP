from datetime import datetime
import time
import logging
import os
import configparser
import requests
import socket
import dotenv

dotenv.load_dotenv()

# Credenciales OpenDNS  save (.env)
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

# Configuración de logging
logging.basicConfig(filename=os.path.splitext(os.path.basename(__file__))[0] + '.log',
                    filemode='a',
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)

logging.getLogger('urllib3').setLevel(logging.CRITICAL)

# Configuración de variables
config_filename = os.path.splitext(os.path.basename(__file__))[0] + '.ini'
config = configparser.ConfigParser()

# Lista de servicios para verificar la IP
check_ip_services = [
    'https://ident.me', 'http://myip.dnsomatic.com', 'https://api.ipify.org', 'https://checkip.amazonaws.com', 'https://ipgrab.io',
    'http://icanhazip.com', 'http://checkip.dyndns.org', 'http://www.trackip.net/ip', 'https://ipapi.co/ip',
    'http://www.cloudflare.com/cdn-cgi/trace', 'http://checkip.dns.he.net', 'http://api.infoip.io'
]


def get_data_time():
    now = datetime.now()
    return now.strftime('%Y-%m-%d %H:%M')


def check_internet_connection(host='www.bing.com', port=80, timeout=5):
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except OSError:
        return False


# Función para obtener la dirección IP actual
def get_current_ip():
    for service in check_ip_services:
        try:
            response = requests.get(service)
            response.raise_for_status()
            ip = response.text.strip()
            return ip

        except requests.HTTPError as e:
            if e.response.status_code == 429:
                logging.info('Too Many Requests: {}.'.format(service))
                print('Too Many Requests: {}.'.format(service))
            else:
                logging.info('HTTP Error: {}'.format(e.response.status_code))
                print('HTTP Error: {}'.format(e.response.status_code))

        except requests.RequestException:
            cont = 0
            while check_internet_connection() == False:
                if cont == 0:
                    logging.info('No connect to internet')
                cont = 1
                print("No connection, retrying in 5 seconds")
                time.sleep(5)

    print('Unable to retrieve the current public IP address. Time')
    logging.info('Unable to connect to servers.')
    time.sleep(60)


# Función para actualizar la IP en OpenDNS
def update_dnsomatic_ip(ip):
    data = {'hostname': 'all.dnsomatic.com', 'myip': ip, 'wildcard': 'NOCHG', 'mx': 'NOCHG', 'backmx': 'NOCHG'}
    url = 'https://updates.dnsomatic.com/nic/update'
    headers = {'User-Agent': username + ' - Home User - 1.0'}
    auth = (username, password)

    try:
        response = requests.get(url, params=data, headers=headers, auth=auth)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        logging.info('Unable to connect to OpenDNS  update service: {}'.format(e))
        print('Unable to connect to OpenDNS  update service. Exiting.')


print("-" * 70)
# Obtener la IP almacenada en el archivo de configuración
try:
    config.read(config_filename)
    stored_ip = config.get('public', 'ipaddress')
    print('The stored IP address from the configuration file is: {}'.format(stored_ip))
except configparser.Error:
    print('Unable to open configuration file.')
    logging.info('Unable to open configuration file.')
    stored_ip = '222.222.222.222'

# Obtener la dirección IP actual
current_ip = get_current_ip()
if current_ip:
    print('The current public IP address is:', current_ip)
else:
    print('Unable to get current public IP address.')

# Verificar si la IP ha cambiado
if stored_ip != current_ip:
    # Actualizar el archivo de configuración con la dirección IP actual
    try:
        config.set('public', 'ipaddress', current_ip)
    except configparser.Error:
        config.add_section('public')
        config.set('public', 'ipaddress', current_ip)
    finally:
        with open(config_filename, 'w') as f:
            config.write(f)

    print(f'{get_data_time()} -- IP address has changed. Updating OpenDNS ...')
    update_result = update_dnsomatic_ip(current_ip)
    if update_result.startswith('good'):
        logging.info('OpenDNS  updated to: {}'.format(update_result.split()[1]))
        print('OpenDNS  updated to: {}'.format(update_result.split()[1]))
        stored_ip = current_ip
    else:
        logging.info('OpenDNS  update failed with error: {}'.format(update_result))
        print('OpenDNS  update failed with error: {}'.format(update_result))
else:
    print(f'{get_data_time()} -- The stored and current IP addresses match. No DNS update necessary.')
