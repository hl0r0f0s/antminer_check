import socket
import json
from accessbot import token, chat_id
import requests


def get_ip():
    '''Get list IP address from file'''
    ip_list = []
    with open('IP_list.txt', 'r') as file:
        for line in file:
            ip_list.append(line)
    return ip_list


def get_temp(ip_list):
        '''Get temperatures from asics and create dict ip:temperature'''
        dict_asics = {}
        for i in ip_list:
            HOST = i
            PORT = 4028        

            m = {"command": "stats"}
            jdata = json.dumps(m)


            try:            
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((HOST, PORT))
                    s.sendall(bytes(jdata,encoding="utf-8"))
                    data = ''
                    while 1:
                        chunk = s.recv(4026)
                        if chunk:
                            data += chunk.decode("utf-8") 
                        else:
                            break
                    datajs = json.loads(data[:-1])
            finally:
                s.close

            temp_chip1 =  datajs.get('STATS')[1].get('temp_chip1')
            temp_chip2 =  datajs.get('STATS')[1].get('temp_chip2')
            temp_chip3 =  datajs.get('STATS')[1].get('temp_chip3')
            temp_chip4 =  datajs.get('STATS')[1].get('temp_chip4')
            temp_max = int(max("-".join([temp_chip1,temp_chip2,temp_chip3,temp_chip4]).split('-')))  # Concatinate all chips, conv to list, find max value
            dict_asics[i] = temp_max
            return dict_asics
        

def send_warning(dict_temp):
    '''Compare temperatures, if above 83C: send message in telegram'''
    for k, v in dict_temp.items():
        if v > 83:
            requests.get('https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '^&text=' + f'[!] Температура асика antminer {k} равна {v} С')


def main():
    send_warning(get_temp(get_ip()))

if __name__ == '__main__':
    main()