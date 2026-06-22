import yaml
import datetime
import os
from ncclient import manager
import xml.etree.ElementTree as ET

# Cargar variables esperadas del archivo centralizado
with open("../vars/vars_005D-21.yaml", "r") as f:
    vars_data = yaml.safe_load(f)

print("=== METADATOS DE EJECUCIÓN NETCONF ===")
print(f"Script: validacion_netconf.py")
print(f"Fecha : {datetime.datetime.now()}")
print(f"Host  : {os.uname()[1]}")
print("======================================\n")

filter_xml = """
<filter>
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <hostname/>
    <interface/>
    <ntp/>
  </native>
</filter>
"""

try:
    print(f"Conectando vía NETCONF (Puerto 830) a {vars_data['router']['ip']}...")
    with manager.connect(
        host=vars_data['router']['ip'],
        port=830,
        username=vars_data['router']['usuario'],
        password=vars_data['router']['password'],
        hostkey_verify=False,
        allow_agent=False,
        look_for_keys=False
    ) as m:
        
        rpc_reply = m.get_config(source='running', filter=filter_xml)
        
        with open("evidencias/rpc_reply_raw.xml", "w") as xml_file:
            xml_file.write(rpc_reply.xml)
        print("-> Archivo XML crudo respaldado en evidencias/rpc_reply_raw.xml\n")
            
        root = ET.fromstring(rpc_reply.xml)
        
        def find_element_text(tree, tag_name):
            elem = tree.find(f".//{{*}}{tag_name}")
            return elem.text if elem is not None else "NO_CONFIGURADO"

        # Extracción de parámetros básicos
        r_hostname = find_element_text(root, "hostname")
        
        # Extracción quirúrgica de NTP basada en tu estructura XML real
        r_ntp = "NO_CONFIGURADO"
        ntp_ip_elem = root.find(".//{*}server-list/{*}ip-address")
        if ntp_ip_elem is not None:
            r_ntp = ntp_ip_elem.text.strip()

        # Descripción WAN (GE1)
        r_desc = "NO_CONFIGURADO"
        for ge in root.findall(".//{*}GigabitEthernet"):
            name_elem = ge.find("{*}name")
            if name_elem is not None and name_elem.text == "1":
                desc_elem = ge.find("{*}description")
                if desc_elem is not None:
                    r_desc = desc_elem.text

        # Parámetros Loopback 10
        r_lb_ip = "NO_CONFIGURADO"
        r_lb_mask = "NO_CONFIGURADO"
        for lb in root.findall(".//{*}Loopback"):
            name_elem = lb.find("{*}name")
            if name_elem is not None and name_elem.text == str(vars_data['router']['loopback_id']):
                addr_elem = lb.find(".//{*}primary/{*}address")
                mask_elem = lb.find(".//{*}primary/{*}mask")
                if addr_elem is not None: r_lb_ip = addr_elem.text
                if mask_elem is not None: r_lb_mask = mask_elem.text

        # Evaluar criterios de compliance
        criterios = {
            "Hostname Corporativo": (r_hostname == vars_data['cliente']['hostname']),
            "Servidor NTP": (r_ntp == vars_data['router']['ntp_server']),
            "Descripción WAN (GE1)": (r_desc == vars_data['router']['descripcion_wan']),
            "IP Loopback 10": (r_lb_ip == vars_data['router']['loopback_ip']),
            "Máscara Loopback 10": (r_lb_mask == vars_data['router']['loopback_mask'])
        }
        
        score = 0
        print("=== REPORTE DE AUDITORÍA DE COMPLIANCE (NETCONF) ===")
        print(f"Hostname detectado : {r_hostname}")
        print(f"NTP Server detectado: {r_ntp}")
        print(f"Descripción detectada: {r_desc}")
        print(f"Loopback IP detec.  : {r_lb_ip} / {r_lb_mask}\n")

        for name, result in criterios.items():
            status = "[OK]" if result else "[FAIL]"
            if result: score += 1
            print(f"Criterio {name.ljust(22)}: {status}")
            
        print("\n------------------------------------------------")
        print(f"RESULTADO GLOBAL: {'CONFORME' if score == 5 else 'NO CONFORME'} ({score}/5 OK)")
        print("------------------------------------------------")

except Exception as e:
    print(f"\n[ERROR] Error inesperado en el procesamiento: {e}")
