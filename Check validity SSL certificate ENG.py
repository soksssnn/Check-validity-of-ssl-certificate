import os, subprocess, re
import requests
from datetime import datetime

def check_file(path: str):
    if os.path.exists(path) == False:
        newfile = open(path,"w+")
        print('Can\'t find \"config.cfg\" let\'s create it:\n')
        token = input('Enter the token you recived from BotFather: ')
        chatid = input('Enter ChatID you want to receive messages: ')
        newfile.write('TOKEN='+ token + '\n' + 'CHATID='+ chatid)
        newfile.close


def send_telegram(text: str, token: str, channel_id: str):   
    url = "https://api.telegram.org/bot"
    url += token
    method = url + "/sendMessage"
    r = requests.post(method, data={
         "chat_id": channel_id,
         "text": text
          })
    if r.status_code != 200:
        raise Exception("post_text error")      

def main():
    check_file('config.cfg')
    cfgfile =open('config.cfg','r+').read()
    token = re.search('TOKEN=(.+?)(?:\n|$)', cfgfile)
    tk = str(token[1])
    channel_id = re.search('CHATID=(.+?)(?:\n|$)', cfgfile)
    chat_id = str(channel_id[1])
    l = 0 
    exp = 0 
    soonexp = 0 
    normal = 0 
    srcpath=input('Enter the path to file with sites: ')
    rfile = open(srcpath, 'r')
    message = ""
    while True:
        line = rfile.readline().rstrip()
        if not line:
            break
        cmd = 'openssl s_client -connect ' + line + ':443 -servername '+ line
        fproc = subprocess.Popen(
             cmd,
             stdout=subprocess.PIPE,
             stderr=subprocess.PIPE
             )
        sproc = subprocess.run(
            ['openssl', 'x509', '-dates'],
            stdin=fproc.stdout,
            stdout=subprocess.PIPE
            )
        l = l + 1    
        regexp = re.search('notAfter=(\S+)\s+(\d+)\s+\S+\s+(\d+)', str(sproc.stdout)) 
        today = datetime.today()
        expdate = regexp[1] + ' ' + regexp[2] +' ' + regexp[3]
        expdatedt = datetime.strptime(expdate, '%b %d %Y')
        result = expdatedt - today
        if result.days < 30:
            if result.days < 0:
                message = message + 'Certificate of ' + line + ' has expired\n'
                exp = exp + 1
            else:
                message = message + 'Certificate of ' + line + ' will expire in ' + str(result.days) +' days\n'
                soonexp = soonexp + 1    
        else:
            message = message + 'Certificate of ' + line + 'does not need an extension, days before the end ' + str(result.days) + '.\n'
            normal = normal + 1
    message = 'A total of ' + str(l) + ' certificates have been verified\n' + str(exp) + ' certificates has expired\n' + str(soonexp) + ' certificates will run out soon\n' + str(normal) + ' - certificates are normal\n' + message

    send_telegram(message, tk, chat_id)       
        




main()
