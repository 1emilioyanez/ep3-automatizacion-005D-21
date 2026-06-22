import requests
import yaml
import json
import urllib3
import datetime
import os

# Desactivar advertencias de certificados auto-firmados del router
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Cargar variables centralizadas
with open("../vars/vars_005D-21.yaml", "r") as f:
    vars_data = yaml.safe_load(f)

print("=== METADATOS DE EJECUCIÓN RESTCONF ===")
print(f"Script: validacion_restconf.py")
print(f"Fecha : {datetime.datetime.now()}")
print(f"Host  : {os.uname()[1]}")
print("======================================\n")

base_url = f"https://{vars_data['router']['ip']}/restconf/data"
auth = (vars_data['router']['usuario'], vars_data['router']['password'])
headers = {"Accept": "application/yang-data+json"}

# Mapeo de Endpoints a consultar en el router
endpoints = {
    "hostname": ("Cisco-IOS-XE-native:native/hostname", "get_hostname.json"),
    "loopback": (f"ietf-interfaces:interfaces/interface=Loopback{vars_data['router']['loopback_id']}", "get_loopback.json"),
    "wan": ("ietf-interfaces:interfaces/interface=GigabitEthernet1", "get_interfaces.json"),
    "ntp": ("Cisco-IOS-XE-native:native/ntp", "get_ntp.json")
}

responses_data = {}

print("Realizando peticiones API RESTCONF...")
for key, (path, filename) in endpoints.items():
    try:
        res = requests.get(f"{base_url}/{path}", auth=auth, headers=headers, verify=False, timeout=10)
        if res.status_code == 200:
            data = res.json()
            responses_data[key] = data
            with open(f"evidencias/responses/{filename}", "w") as f_out:
                json.dump(data, f_out, indent=2)
        else:
            print(f"-> Advertencia: Error {res.status_code} al consultar endpoint {key}")
    except Exception as e:
        print(f"-> Error conectando al endpoint {key}: {e}")

print("-> Archivos JSON crudos respaldados en evidencias/responses/\n")

# Función auxiliar para buscar llaves de forma recursiva (para NTP y Hostname)
def buscar_valor_por_llave(data, target_key):
    if isinstance(data, dict):
        if target_key in data:
            return data[target_key]
        for v in data.values():
            item = buscar_valor_por_llave(v, target_key)
            if item is not None: return item
    elif isinstance(data, list):
        for v in data:
            item = buscar_valor_por_llave(v, target_key)
            if item is not None: return item
    return None

# Procesar y validar la data JSON devuelta por el router
try:
    # 1. Validar Hostname
    r_host = buscar_valor_por_llave(responses_data.get('hostname', {}), 'hostname')
    if r_host is None: r_host = responses_data.get('hostname', {}).get('Cisco-IOS-XE-native:hostname', "FAIL")
    v_host = r_host == vars_data['cliente']['hostname']
    
    # 2. Validar NTP Server
    r_ntp = buscar_valor_por_llave(responses_data.get('ntp', {}), 'ip-address')
    if r_ntp is None: r_ntp = "NO_CONFIGURADO"
    v_ntp = str(r_ntp) == str(vars_data['router']['ntp_server'])
    
    # 3. Validar Descripción WAN
    r_desc = responses_data.get('wan', {}).get('ietf-interfaces:interface', {}).get('description', 'NO_CONFIGURADO')
    v_desc = r_desc == vars_data['router']['descripcion_wan']
    
    # 4. Validar IP y Máscara Loopback usando tu estructura exacta confirmada
    r_ip = "NO_CONFIGURADO"
    r_mask = "NO_CONFIGURADO"
    
    lb_interface = responses_data.get('loopback', {}).get('ietf-interfaces:interface', {})
    ipv4_block = lb_interface.get('ietf-ip:ipv4', {})
    address_list = ipv4_block.get('address', [])
    
    if address_list:
        r_ip = address_list[0].get('ip', 'NO_CONFIGURADO')
        r_mask = address_list[0].get('netmask', 'NO_CONFIGURADO')

    v_ip = r_ip == vars_data['router']['loopback_ip']
    v_mask = r_mask == vars_data['router']['loopback_mask']
    
    criterios = {
        "Hostname Corporativo": v_host,
        "Servidor NTP": v_ntp,
        "Descripción WAN (GE1)": v_desc,
        "Dirección IP Loopback": v_ip,
        "Máscara Loopback": v_mask
    }
    
    score = sum(criterios.values())
    print("=== REPORTE DE AUDITORÍA DE COMPLIANCE (RESTCONF) ===")
    print(f"Hostname detectado  : {r_host}")
    print(f"NTP Server detectado : {r_ntp}")
    print(f"Descripción detectada : {r_desc}")
    print(f"Loopback IP detec.   : {r_ip} / {r_mask}\n")

    for k, v in criterios.items():
        print(f"Criterio {k.ljust(22)}: {'[OK]' if v else '[FAIL]'}")
        
    print("\n------------------------------------------------")
    print(f"RESULTADO GLOBAL: {'CONFORME' if score == 5 else 'NO CONFORME'} ({score}/5 OK)")
    print("------------------------------------------------")

except Exception as e:
    print(f"[ERROR] Error inesperado procesando el JSON: {e}")
