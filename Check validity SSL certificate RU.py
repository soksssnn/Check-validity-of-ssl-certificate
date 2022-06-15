import os, subprocess, re, requests
from datetime import datetime

def check_file(path: str):
    if os.path.exists(path) == False:
        newfile = open(path,"w+")
        print('Не найден файл с данными о телеграм боте, давайте заполним его: ')
        token = input('Введите Api token который вам дал BotFather: ')
        chatid = input('Введите chatid куда вы хотите получить конечный результат: ')
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
    l = 0 #Кол-во строк
    exp = 0 #Кол-во просроченных сертификатов
    soonexp = 0 #Кол-во сертификатов жить которым меньше 30 дней
    normal = 0 #Кол-во сертификатов которым больше 30 дней до окончания
    srcpath=input('Введите путь до файла с сайтами: ')
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
                message = message + 'Сертификат сайта ' + line + ' уже закончился\n'
                exp = exp + 1
            else:
                message = message + 'Сертификат сайта ' + line + ' закончится через ' + str(result.days) +' дней.\n'
                soonexp = soonexp + 1    
        else:
            message = message + 'Сертификат сайта ' + line + ' в продлении не нуждается, дней до окончания ' + str(result.days) + '.\n'
            normal = normal + 1
    message = 'Всего проверено ' + str(l) + ' сертификатов из которых:\n' + str(exp) + ' - просрочены\n' + str(soonexp) + ' - скоро закончатся\n' + str(normal) + ' - не требуют продления\n' + message

    send_telegram(message, tk, chat_id)       
        




main()
