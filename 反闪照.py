import websocket
from requests import get
from json import loads
from re import findall
from yaml import load,FullLoader
host = {}
for s in load(open('config.yml',encoding='utf-8').read(),Loader=FullLoader)['servers']:
    if 'http' in s:
        host['http'] = f"http://{s['http']['host']}:{s['http']['port']}/"
    elif 'ws' in s:
        host['ws'] = f"ws://{s['ws']['host']}:{s['ws']['port']}"
print(host)
SELF_ID = None
call_api = lambda api_name,**data:loads(get(host['http']+api_name+'?'+'&'.join(f"{k}={v}" for k,v in data.items())).content)

def on_message(ws,message):
    data = loads(message)
    if data['post_type'] == 'meta_event':
        if data['meta_event_type'] == 'lifecycle':
            global SELF_ID
            SELF_ID = data['self_id']
            call_api('send_msg',user_id=SELF_ID,message='反闪照开启')
    
    elif data['post_type']=='message':
        if 'type=flash' in data['message']:
            url = f"https://gchat.qpic.cn/gchatpic_new/{data['sender']['user_id']}/2640570090-2264725042-{findall('file=(.*?).image',data['message']).pop().upper()}/0?term=3"
            res = call_api("send_msg",user_id=SELF_ID,message=f"来自{data['sender']['nickname']}的闪照[CQ:image,file={url}]")
def on_error(ws,error):
    pass
def on_close(*args):
    pass

def start_listening():
    ws = websocket.WebSocketApp(host['ws'],on_message=on_message,on_error=on_error,on_close=on_close)
    while True:
        try:
            ws.run_forever()
        except Exception as e:
            pass

if __name__ == "__main__":
    from subprocess import Popen
    proc = Popen(['go-cqhttp_windows_amd64.exe','-faststart'])
    start_listening()
