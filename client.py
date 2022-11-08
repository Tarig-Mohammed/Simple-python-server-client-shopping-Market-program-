import socket
if __name__ == '__main__':
    try:
        # init socket
        host = '127.0.0.1'  # server address
        # which is your preference for performing text analysis
        port = 5000  # server port
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # set TCP IP4 connection
        clientSocket.setblocking(True)
        socket.setdefaulttimeout(60 * 2)  # set default blocking time to 5 minutes for all operations
        clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 3500)  # set receive buffer size
        clientSocket.connect((host, port))  # connect to server
        mn = clientSocket.recv(3500).decode()  # receive response from server for first time
        while True:
            try:
                print(mn)
                data = input('You>>')  # get user request
                if not data:
                    continue
                elif data.isnumeric():
                    data = str(socket.htonl(int(data)))
                clientSocket.send(data.encode())  # send user request to server
                if data.strip().lower() == 'x':  # check if request is end connection
                    break  # break while loop
            except TimeoutError as e:
                continue
            except ConnectionError as e:
                print(str(f'Connection Ended'))
                break
            except KeyboardInterrupt as e:
                print(str(f'KIE {e}'))
                continue
            mn = clientSocket.recv(3500).decode()  # receive response from server

        clientSocket.close()  # end connection
    except ConnectionError as e:
        print(str(f'CE Connection Ended'))
    except socket.error as e:
        print(str(f'SE {e}'))
    except Exception as e:
        print(str(f'E {e}'))
