# Informe Técnico de Automatización e Implementación de Compliance

## 1. Objetivo del proyecto
El presente proyecto detalla la implementación automatizada y la auditoría de cumplimiento (*compliance*) de un nuevo enrutador de borde para la empresa cliente **Editorial Austral SA**. El objetivo principal fue realizar el ciclo completo de documentación, aprovisionamiento y verificación independiente de variables corporativas utilizando herramientas programáticas para mitigar errores humanos y optimizar los tiempos de despliegue.

## 2. Alcance
* **Dentro del alcance:** Respaldo automatizado de estados iniciales, habilitación de servicios programáticos de red (NETCONF y RESTCONF), aprovisionamiento de identidad (*hostname*), banners de acceso restringido, sincronización temporal vía NTP, e instanciación de direccionamiento IP en interfaces virtuales (Loopback) y descripciones WAN físicas.
* **Fuera del alcance:** Configuración de protocolos de enrutamiento dinámico (OSPF/BGP), túneles VPN de respaldo y políticas de seguridad perimetral avanzadas (ACLs/Firewalling).

## 3. Infraestructura utilizada
* **Estación de Trabajo:** DEVASC VM (Ambiente virtualizado Linux Ubuntu).
* **Dispositivo de Red:** Cisco CSR1kv (Sistema Operativo Cisco IOS-XE Software).
* **Orquestadores y Herramientas:** Ansible Core, pyATS / Cisco Genie Engine, Python 3.

## 4. Tecnologías empleadas y justificación
* **pyATS / Genie:** Se utilizó en las Fases 1 y 5 para extraer de forma estructurada e independiente los estados de los objetos de red vía SSH y realizar análisis comparativos semánticos (*diff*), garantizando una auditoría transparente.
* **Ansible:** Se seleccionó para la Fase 2 debido a su arquitectura sin agentes y su capacidad de aplicar configuraciones estandarizadas e *idempotentes* de manera masiva y ágil.
* **NETCONF:** Protocolo seguro basado en codificación XML implementado en la Fase 3 para auditar desde un script externo el árbol completo de la configuración en ejecución.
* **RESTCONF:** Interfaz API basada en HTTPS utilizada en la Fase 4 para consumir recursos específicos y granulares en formato ligero JSON, ideal para integraciones ágiles de monitoreo.

## 5. Configuración aplicada
* **Empresa Cliente:** Editorial Austral SA
* **Hostname Corporativo:** RTR-EDITAUS
* **IP Loopback de Gestión:** 10.5.21.1
* **Máscara Loopback:** 255.255.255.0
* **Descripción Interfaz WAN:** Enlace-WAN-Tocopilla
* **Banner de Acceso:** ACCESO RESTRINGIDO - EDITAUS
* **Servidor NTP:** 1.1.1.1

## 6. Resultados de validación
| Criterio Verificado | Protocolo | Estado | Resultado |
| :--- | :--- | :--- | :--- |
| Configuración de Identidad (Hostname) | NETCONF / RESTCONF | [OK] | CONFORME |
| Identificación Interfaz WAN (GE1) | NETCONF / RESTCONF | [OK] | CONFORME |
| Sincronización Temporal (NTP) | NETCONF / RESTCONF | [OK] | CONFORME |
| Segmento Loopback 10 (IP / Mask) | NETCONF / RESTCONF | [OK] | CONFORME |

## 7. Conclusiones
La automatización del ciclo de vida del dispositivo concluyó de manera exitosa. Se verificó con un 100% de efectividad la conformidad del equipo bajo dos protocolos programáticos independientes, quedando el enrutador validado de forma transparente y disponible para pasar de forma segura a operaciones de producción.
