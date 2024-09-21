import sys, os, socket, threading, time
from scapy.all import *
from urllib.parse import urlparse

_ports = []
_alive = 0

def _scan(_ip, _prt, _wait, _time, abort_event):
    global _ports, _alive
    
    _alive +=1
    try:
        # craft SYN stealth packet
        response = sr1(IP(dst=_ip)/TCP(dport=int(_prt), flags="S"), timeout=int(_time), verbose=0)
        
        if response and response.haslayer(TCP):
            if response[TCP].flags == 0x12:
                print('\033[22m\033[32m---> CONNECTION OPEN @ ' + _ip + ':' + str(_prt))
            else:
                # non-compliant response received
                _ports.remove(int(_prt))
        else:
            # connection rejected
            _ports.remove(int(_prt))
    except:
        print('\033[1m\033[31mCritical error encountered crafting SYN packet!')
        _ports.remove(int(_prt))
    finally:
        # close the hanging socket with a RST
        try:
            _reset = IP(dst=ip)/TCP(dport=int(_prt), flags="R")
            send(_reset, verbose=False)
        except:
            pass
        
    # sleep for x amount of milliseconds
    start_time = time.perf_counter()
    while (time.perf_counter() - start_time) * 1000 < int(_wait):
        if abort_event.is_set():
            break
    
    _alive -=1
    

def _rslv(_host):
    # format entry as URI class. works for both IP addresses and hostnames
    if not (_host.lower().startswith('http://') or _host.lower().startswith('https://')):
        _host = 'http://' + _host
    
    # extract domain from URL / resolve IP
    try:
        _domain = urlparse(_host).netloc
        _ip = socket.gethostbyname(_domain)
        return _ip
    except:
        sys.exit(' \033[1m\033[31mDNS resolution error! Exiting...\r\n')

def main():
    # confirm script elevation
    if not os.getegid() == 0:
        sys.exit('\r\n   \033[1m\033[33mScript requires root elevation!\r\n')
    
    global _ports, _alive
    os.system('clear')
    print('''\033[22m\033[37m
  _____ _         _              _____                ___     ___ 
 |   __| |_ ___ _| |___ _ _ _   |   __|___ ___ ___   |_  |   |   |
 |__   |   | . | . | . | | | |  |__   |  _| . |   |   _| |_ _| | |
 |_____|_|_|_|_|___|___|_____|  |_____|___|_|_|_|_|  |_____|_|___|    
''')
    # capture user input
    try:
        # resolve hostname
        _host = input(' \033[22m\033[37mEnter IP/site to scan:\033[1m\033[37m ')
        _ip = _rslv(_host)
        
        print('\r\n \033[22m\033[37mEnter in port(s) to scan. Can be a single port')
        print(' or from a range of ports, ex: "1-1024". Enter "exit"')
        print(' when finished.\r\n')
        
        _done = False
        while _done != True:
            _prt = input(' \033[22m\033[37mPort/range>\033[1m\033[37m ')
            
            if _prt == 'exit':
                _done = True
            elif '-' in _prt:
                # add range to list
                try:
                    _min, _max = _prt.split('-')
                    if int(_min) > int(_max):
                        _min = _max
                    
                    # add range to list
                    for _ in range(int(_min), int(_max)):
                        _ports.append(_)
                except:
                    pass
            else:
                # add single port to list
                _ports.append(int(_prt))
        
        if len(_ports) == 0:
            # ensure an empty list is not scanned
            sys.exit(' \033[22m\033[37mAt least one port must be specified! Exiting...\r\n')
            
        _thdz = input('\r\n \033[22m\033[37m# of threads (default=5):\033[1m\033[37m ')
        _time = input(' \033[22m\033[37mTimeout sec (default=1):\033[1m\033[37m ')
        _wait = input(' \033[22m\033[37mSleep in M/s (default=100):\033[1m\033[37m ')
        
        input('\r\n \033[22m\033[37mReady? Strike <ENTER> to launch and <CTRL+C> to abort...')
        
        print('\r\n Scanning! Please stand-by\r\n')
        
        # remove list duplicates / order ports from lst to grtst
        _ports = list(set(_ports))
        _ports = sorted(_ports)
    except KeyboardInterrupt:
        sys.exit('\r\n \033[1m\033[37mAborted!\r\n')

    # manage thread/scan execution
    abort_event = threading.Event()
    try:    
        for _prt in _ports:
            while True:
                if _alive != int(_thdz):
                    x = threading.Thread(target=_scan, args=(_ip, _prt, _wait, _time, abort_event))
                    x.daemonized = True
                    x.start()
                    break
    except KeyboardInterrupt:
        abort_event.set()
        
    # wait till threads power off
    while True:
        if _alive == 0:
            break
    
    # dump alive ports to .txt
    try:
        chs = input('\r\n \033[22m\033[37mDump valid ports to textfile? Y/n: ')
        if (chs.lower() == 'y' or chs.lower() == 'yes'):
            with open('ports.txt', 'w') as file:
                for item in _ports:
                    file.write(str(item) + '\n')
            file.close()
            print('\r\n Dumped to file "ports.txt"\r\n')
    except KeyboardInterrupt:
        pass
    except:
        pass    
    
    sys.exit('\r\n \033[1m\033[37mThank you for using Shadow Scanner 1.0 :)')

if __name__ == '__main__':
    main()
