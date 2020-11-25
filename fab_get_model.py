import pysftp #pip install pysftp
import json
import paho.mqtt.client as mqtt #pip install paho-mqtt
import paho.mqtt.publish as publish
import os
import datetime
import traceback
# *********************************************************************
# Config

MQTT_SERVER = os.getenv('MQTT_SERVER') if os.getenv('MQTT_SERVER') else "qa.mqtt.idi-plus.com"  
MQTT_PORT = int(os.getenv('MQTT_PORT')) if os.getenv('MQTT_PORT') else 1883  
MQTT_ALIVE = int(os.getenv('MQTT_ALIVE')) if os.getenv('MQTT_ALIVE') else 60  
MQTT_TOPIC = os.getenv('MQTT_TOPIC') if os.getenv('MQTT_TOPIC') else "/123/123" 
NFS_SERVER = os.getenv('NFS_SERVER') if os.getenv('NFS_SERVER') else "13.57.162.188"
NFS_PORT = int(os.getenv('NFS_PORT')) if os.getenv('NFS_PORT') else 32222
USER = os.getenv('USER') if os.getenv('USER') else "models"
PASSWD = os.getenv('PASSWD') if os.getenv('PASSWD') else "liteonmodels"
LOCAL_PATH = os.getenv('LOCAL_PATH') if os.getenv('LOCAL_PATH') else "./"

def on_connect(client, userdata, flags, rc):
    #subscribe topic
    try:
      client.subscribe(MQTT_TOPIC)
    except Exception as e:
      print(e)
      publish.single(MQTT_TOPIC+'/res',json.dumps({'code':'0','msg':str(e),'topic':MQTT_TOPIC}),hostname=MQTT_SERVER,port=MQTT_PORT)
      with open('log.txt', 'a+') as f:
        print(datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')+"\n type error: " + str(e), file=f)
        print(traceback.format_exc(), file=f)

def on_message(client, userdata, message):
  try:
    payload =bytes.decode(message.payload)
    payload_list = json.loads(payload)
    msg = json.loads(payload_list['message'])
    model_path = msg['model_path']
    subject = msg['subject']
    model_version = msg['model_version']
    #get model extension
    model_extension = os.path.splitext(model_path)[1]
    model_extension = model_extension if len(model_extension.split('_')) == 1 else model_extension.split('_')[0]
    #origin filename
    # origin_filename = (os.path.splitext(model_path)[0]).split('/')[-1] + model_extension
    local_model_path = LOCAL_PATH+subject+'/'+subject+model_extension

    #get model
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(NFS_SERVER,port=NFS_PORT, username=USER, password=PASSWD,cnopts=cnopts) as sftp:
      print(model_path)
      if(sftp.isfile(model_path)):
        print("copy model from",model_path)
        print('LOCAL_PATH',LOCAL_PATH+subject)
        if not os.path.isdir(LOCAL_PATH+subject):
          os.mkdir(LOCAL_PATH+subject)

        #sftp get model
        print('local_model_path',local_model_path)
        sftp.get(model_path,localpath=local_model_path)
        print("Success copy")
        client.publish(MQTT_TOPIC+'/res', json.dumps({'code':'1','msg':'success','topic':MQTT_TOPIC}))
        sftp.close()
        print(model_version)
        print(LOCAL_PATH+subject+'/'+subject)
        fp = open(LOCAL_PATH+subject+'/'+subject,'w')
        fp.write(model_version)
        fp.close()

      else:
      #exception file does not exist
        sftp.close()
        raise FileExistsError(model_path + 'file does not exist')
      

      
  except Exception as e:
    print(e)
    publish.single(MQTT_TOPIC+'/res',json.dumps({'code':'0','msg':str(e),'topic':MQTT_TOPIC}),hostname=MQTT_SERVER,port=MQTT_PORT)
    with open('log.txt', 'a+') as f:
      print(datetime.datetime.now().strftime(
          '%Y-%m-%d %H:%M:%S')+"\n type error: " + str(e), file=f)
      print(traceback.format_exc(), file=f)
      
    


if __name__ == '__main__':
  client = mqtt.Client()
  client.on_connect = on_connect
  client.on_message = on_message
  #connect mqtt broker
  client.connect(MQTT_SERVER, MQTT_PORT, MQTT_ALIVE)
  while True:
    try:
      client.loop_forever()
    except KeyboardInterrupt:
        print('close')
        client.disconnect()
        exit(0)
    except Exception as e:
      print(e)
      publish.single(MQTT_TOPIC,json.dumps({'code':'0','msg':str(e),'topic':MQTT_TOPIC}),hostname=MQTT_SERVER,port=MQTT_PORT)
      with open('log.txt', 'a+') as f:
        print(datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')+"\n type error: " + str(e), file=f)
        print(traceback.format_exc(), file=f)