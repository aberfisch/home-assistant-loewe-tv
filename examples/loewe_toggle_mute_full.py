{\rtf1\ansi\ansicpg1252\cocoartf2867
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset0 Menlo-Bold;\f1\fnil\fcharset0 Menlo-Regular;}
{\colortbl;\red255\green255\blue255;\red56\green185\blue199;\red0\green0\blue0;\red57\green192\blue38;
\red202\green51\blue35;\red86\green32\blue244;\red219\green39\blue218;}
{\*\expandedcolortbl;;\cssrgb\c25546\c77007\c82023;\csgray\c0;\cssrgb\c25706\c77963\c19557;
\cssrgb\c83899\c28663\c18026;\cssrgb\c41681\c25958\c96648;\cssrgb\c89513\c29736\c88485;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\pardirnatural\partightenfactor0

\f0\b\fs22 \cf2 \CocoaLigature0 import
\f1\b0 \cf3  http.client\

\f0\b \cf2 import
\f1\b0 \cf3  xml.etree.ElementTree 
\f0\b \cf2 as
\f1\b0 \cf3  ET\

\f0\b \cf2 import
\f1\b0 \cf3  time\

\f0\b \cf2 import
\f1\b0 \cf3  random\
\
host = 
\f0\b \cf4 "192.168.79.35"
\f1\b0 \cf3 \
port = 905\
path = 
\f0\b \cf4 "/loewe_tablet_0001"
\f1\b0 \cf3 \
namespace = 
\f0\b \cf4 "urn:loewe.de:RemoteTV:Tablet"
\f1\b0 \cf3 \
\
fcid = str(random.randint(10000000, 99999999))\
device_type = 
\f0\b \cf4 "Tablet"
\f1\b0 \cf3 \
device_name = 
\f0\b \cf4 "PythonDevice"
\f1\b0 \cf3 \
device_uuid = 
\f0\b \cf4 "dc:a6:32:3f:f1:8a"
\f1\b0 \cf3 \
requester_name = 
\f0\b \cf4 "PythonApp"
\f1\b0 \cf3 \
\
MUTE_KEYCODE = 13 
\f0\b \cf5  # Loewe remote control keycode for Mute toggle
\f1\b0 \cf3 \
\

\f0\b \cf2 def\cf6  request_access
\f1\b0 \cf3 ():\
    soap_body = f
\f0\b \cf4 """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
\f1\b0 \cf3 \

\f0\b \cf4         xmlns:ltv="\{namespace\}">
\f1\b0 \cf3 \

\f0\b \cf4       <soapenv:Header/>
\f1\b0 \cf3 \

\f0\b \cf4       <soapenv:Body>
\f1\b0 \cf3 \

\f0\b \cf4         <ltv:RequestAccess>
\f1\b0 \cf3 \

\f0\b \cf4           <ltv:fcid>\{fcid\}</ltv:fcid>
\f1\b0 \cf3 \

\f0\b \cf4           <ltv:DeviceType>\{device_type\}</ltv:DeviceType>
\f1\b0 \cf3 \

\f0\b \cf4           <ltv:DeviceName>\{device_name\}</ltv:DeviceName>
\f1\b0 \cf3 \

\f0\b \cf4           <ltv:DeviceUUID>\{device_uuid\}</ltv:DeviceUUID>
\f1\b0 \cf3 \

\f0\b \cf4           <ltv:RequesterName>\{requester_name\}</ltv:RequesterName>
\f1\b0 \cf3 \

\f0\b \cf4         </ltv:RequestAccess>
\f1\b0 \cf3 \

\f0\b \cf4       </soapenv:Body>
\f1\b0 \cf3 \

\f0\b \cf4     </soapenv:Envelope>
\f1\b0 \cf3 \

\f0\b \cf4     """
\f1\b0 \cf3 \
    headers = \{\
        
\f0\b \cf4 "Content-Type"
\f1\b0 \cf3 : 
\f0\b \cf4 "text/xml; charset=utf-8"
\f1\b0 \cf3 ,\
        
\f0\b \cf4 "SOAPAction"
\f1\b0 \cf3 : 
\f0\b \cf4 '"urn:loewe.de:RemoteTV:Tablet#RequestAccess"'
\f1\b0 \cf3 \
    \}\
    
\f0\b \cf2 while
\f1\b0 \cf3  
\f0\b \cf7 True
\f1\b0 \cf3 :\
        
\f0\b \cf2 try
\f1\b0 \cf3 :\
            conn = http.client.HTTPConnection(host, port, timeout=5)\
            conn.request(
\f0\b \cf4 "POST"
\f1\b0 \cf3 , path, body=soap_body, headers=headers)\
            response = conn.getresponse()\
            resp_text = response.read().decode(
\f0\b \cf4 'utf-8'
\f1\b0 \cf3 , errors=
\f0\b \cf4 'ignore'
\f1\b0 \cf3 )\
            conn.close()\
        
\f0\b \cf2 except
\f1\b0 \cf3  Exception 
\f0\b \cf2 as
\f1\b0 \cf3  e:\
            print(f
\f0\b \cf4 "Error connecting: \{e\}"
\f1\b0 \cf3 )\
            time.sleep(3)\
            
\f0\b \cf2 continue
\f1\b0 \cf3 \
\
        
\f0\b \cf2 try
\f1\b0 \cf3 :\
            root = ET.fromstring(resp_text)\
            ns = \{
\f0\b \cf4 "ltv"
\f1\b0 \cf3 : namespace\}\
            status = root.find(
\f0\b \cf4 ".//ltv:AccessStatus"
\f1\b0 \cf3 , ns)\
            clientid = root.find(
\f0\b \cf4 ".//ltv:ClientId"
\f1\b0 \cf3 , ns)\
            
\f0\b \cf2 if
\f1\b0 \cf3  status 
\f0\b \cf2 is
\f1\b0 \cf3  
\f0\b \cf2 not
\f1\b0 \cf3  
\f0\b \cf7 None
\f1\b0 \cf3 :\
                status_text = status.text\
                
\f0\b \cf2 if
\f1\b0 \cf3  status_text == 
\f0\b \cf4 "Accepted"
\f1\b0 \cf3  
\f0\b \cf2 and
\f1\b0 \cf3  clientid 
\f0\b \cf2 is
\f1\b0 \cf3  
\f0\b \cf2 not
\f1\b0 \cf3  
\f0\b \cf7 None
\f1\b0 \cf3 :\
                    
\f0\b \cf2 return
\f1\b0 \cf3  clientid.text\
                
\f0\b \cf2 elif
\f1\b0 \cf3  status_text == 
\f0\b \cf4 "Denied"
\f1\b0 \cf3 :\
                    print(
\f0\b \cf4 "Pairing denied. Exiting."
\f1\b0 \cf3 )\
                    
\f0\b \cf2 return
\f1\b0 \cf3  
\f0\b \cf7 None
\f1\b0 \cf3 \
                
\f0\b \cf2 elif
\f1\b0 \cf3  status_text == 
\f0\b \cf4 "Pending"
\f1\b0 \cf3 :\
                    print(
\f0\b \cf4 "Please accept pairing on the TV. Retrying in 3 seconds..."
\f1\b0 \cf3 )\
                    time.sleep(3)\
                
\f0\b \cf2 else
\f1\b0 \cf3 :\
                    print(
\f0\b \cf4 "Unexpected status. Retrying in 3 seconds..."
\f1\b0 \cf3 )\
                    time.sleep(3)\
            
\f0\b \cf2 else
\f1\b0 \cf3 :\
                print(
\f0\b \cf4 "No status found in response. Retrying in 3 seconds..."
\f1\b0 \cf3 )\
                time.sleep(3)\
        
\f0\b \cf2 except
\f1\b0 \cf3  Exception 
\f0\b \cf2 as
\f1\b0 \cf3  e:\
            print(
\f0\b \cf4 "Error parsing XML:"
\f1\b0 \cf3 , e)\
            print(resp_text)\
            time.sleep(3)\
\

\f0\b \cf2 def\cf6  send_mute_toggle
\f1\b0 \cf3 (clientid):\
   
\f0\b \cf5  # Loewe RC key event sequence: press and release MUTE key
\f1\b0 \cf3 \
    soap_body = f
\f0\b \cf4 """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
\f1\b0 \cf3 \

\f0\b \cf4         xmlns:ltv="\{namespace\}">
\f1\b0 \cf3 \

\f0\b \cf4       <soapenv:Header/>
\f1\b0 \cf3 \

\f0\b \cf4       <soapenv:Body>
\f1\b0 \cf3 \

\f0\b \cf4         <ltv:InjectRCKey>
\f1\b0 \cf3 \

\f0\b \cf4           <ltv:fcid>\{fcid\}</ltv:fcid>
\f1\b0 \cf3 \

\f0\b \cf4           <ltv:ClientId>\{clientid\}</ltv:ClientId>
\f1\b0 \cf3 \

\f0\b \cf4           <ltv:InputEventSequence>
\f1\b0 \cf3 \

\f0\b \cf4             <ltv:RCKeyEvent alphabet="l2700" value="\{MUTE_KEYCODE\}" mode="press"/>
\f1\b0 \cf3 \

\f0\b \cf4             <ltv:RCKeyEvent alphabet="l2700" value="\{MUTE_KEYCODE\}" mode="release"/>
\f1\b0 \cf3 \

\f0\b \cf4           </ltv:InputEventSequence>
\f1\b0 \cf3 \

\f0\b \cf4         </ltv:InjectRCKey>
\f1\b0 \cf3 \

\f0\b \cf4       </soapenv:Body>
\f1\b0 \cf3 \

\f0\b \cf4     </soapenv:Envelope>
\f1\b0 \cf3 \

\f0\b \cf4     """
\f1\b0 \cf3 \
    headers = \{\
        
\f0\b \cf4 "Content-Type"
\f1\b0 \cf3 : 
\f0\b \cf4 "text/xml; charset=utf-8"
\f1\b0 \cf3 ,\
        
\f0\b \cf4 "SOAPAction"
\f1\b0 \cf3 : 
\f0\b \cf4 '"urn:loewe.de:RemoteTV:Tablet#InjectRCKey"'
\f1\b0 \cf3 \
    \}\
    
\f0\b \cf2 try
\f1\b0 \cf3 :\
        conn = http.client.HTTPConnection(host, port, timeout=5)\
        conn.request(
\f0\b \cf4 "POST"
\f1\b0 \cf3 , path, body=soap_body, headers=headers)\
        response = conn.getresponse()\
        resp_text = response.read().decode(
\f0\b \cf4 'utf-8'
\f1\b0 \cf3 , errors=
\f0\b \cf4 'ignore'
\f1\b0 \cf3 )\
        conn.close()\
        print(
\f0\b \cf4 "Mute toggle RCKey response:"
\f1\b0 \cf3 )\
        print(resp_text)\
    
\f0\b \cf2 except
\f1\b0 \cf3  Exception 
\f0\b \cf2 as
\f1\b0 \cf3  e:\
        print(f
\f0\b \cf4 "Error sending RCKey for Mute: \{e\}"
\f1\b0 \cf3 )\
\

\f0\b \cf2 if
\f1\b0 \cf3  __name__ == 
\f0\b \cf4 "__main__"
\f1\b0 \cf3 :\
    print(f
\f0\b \cf4 "FCID: \{fcid\}"
\f1\b0 \cf3 )\
    print(
\f0\b \cf4 "Requesting pairing..."
\f1\b0 \cf3 )\
    clientid = request_access()\
    
\f0\b \cf2 if
\f1\b0 \cf3  clientid:\
        print(f
\f0\b \cf4 "ClientId: \{clientid\}"
\f1\b0 \cf3 )\
        print(
\f0\b \cf4 "Sending mute toggle command..."
\f1\b0 \cf3 )\
        send_mute_toggle(clientid)\
    
\f0\b \cf2 else
\f1\b0 \cf3 :\
        print(
\f0\b \cf4 "Pairing failed or denied."
\f1\b0 \cf3 )\
\
}