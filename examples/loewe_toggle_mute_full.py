import http.client
import xml.etree.ElementTree as ET
import time
import random

host = "192.168.79.35"
port = 905
path = "/loewe_tablet_0001"
namespace = "urn:loewe.de:RemoteTV:Tablet"

fcid = str(random.randint(10000000, 99999999))
device_type = "Tablet"
device_name = "PythonDevice"
device_uuid = "dc:a6:32:3f:f1:8a"
requester_name = "PythonApp"

MUTE_KEYCODE = 13  # Loewe remote control keycode for Mute toggle

def request_access():
    soap_body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:ltv="{namespace}">
      <soapenv:Header/>
      <soapenv:Body>
        <ltv:RequestAccess>
          <ltv:fcid>{fcid}</ltv:fcid>
          <ltv:DeviceType>{device_type}</ltv:DeviceType>
          <ltv:DeviceName>{device_name}</ltv:DeviceName>
          <ltv:DeviceUUID>{device_uuid}</ltv:DeviceUUID>
          <ltv:RequesterName>{requester_name}</ltv:RequesterName>
        </ltv:RequestAccess>
      </soapenv:Body>
    </soapenv:Envelope>
    """
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": '"urn:loewe.de:RemoteTV:Tablet#RequestAccess"'
    }
    while True:
        try:
            conn = http.client.HTTPConnection(host, port, timeout=5)
            conn.request("POST", path, body=soap_body, headers=headers)
            response = conn.getresponse()
            resp_text = response.read().decode('utf-8', errors='ignore')
            conn.close()
        except Exception as e:
            print(f"Error connecting: {e}")
            time.sleep(3)
            continue

        try:
            root = ET.fromstring(resp_text)
            ns = {"ltv": namespace}
            status = root.find(".//ltv:AccessStatus", ns)
            clientid = root.find(".//ltv:ClientId", ns)
            if status is not None:
                status_text = status.text
                if status_text == "Accepted" and clientid is not None:
                    return clientid.text
                elif status_text == "Denied":
                    print("Pairing denied. Exiting.")
                    return None
                elif status_text == "Pending":
                    print("Please accept pairing on the TV. Retrying in 3 seconds...")
                    time.sleep(3)
                else:
                    print("Unexpected status. Retrying in 3 seconds...")
                    time.sleep(3)
            else:
                print("No status found in response. Retrying in 3 seconds...")
                time.sleep(3)
        except Exception as e:
            print("Error parsing XML:", e)
            print(resp_text)
            time.sleep(3)

def send_mute_toggle(clientid):
    # Loewe RC key event sequence: press and release MUTE key
    soap_body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:ltv="{namespace}">
      <soapenv:Header/>
      <soapenv:Body>
        <ltv:InjectRCKey>
          <ltv:fcid>{fcid}</ltv:fcid>
          <ltv:ClientId>{clientid}</ltv:ClientId>
          <ltv:InputEventSequence>
            <ltv:RCKeyEvent alphabet="l2700" value="{MUTE_KEYCODE}" mode="press"/>
            <ltv:RCKeyEvent alphabet="l2700" value="{MUTE_KEYCODE}" mode="release"/>
          </ltv:InputEventSequence>
        </ltv:InjectRCKey>
      </soapenv:Body>
    </soapenv:Envelope>
    """
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": '"urn:loewe.de:RemoteTV:Tablet#InjectRCKey"'
    }
    try:
        conn = http.client.HTTPConnection(host, port, timeout=5)
        conn.request("POST", path, body=soap_body, headers=headers)
        response = conn.getresponse()
        resp_text = response.read().decode('utf-8', errors='ignore')
        conn.close()
        print("Mute toggle RCKey response:")
        print(resp_text)
    except Exception as e:
        print(f"Error sending RCKey for Mute: {e}")

if __name__ == "__main__":
    print(f"FCID: {fcid}")
    print("Requesting pairing...")
    clientid = request_access()
    if clientid:
        print(f"ClientId: {clientid}")
        print("Sending mute toggle command...")
        send_mute_toggle(clientid)
    else:
        print("Pairing failed or denied.")



