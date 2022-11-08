import socket
import threading

serverTurnedOn = False

# set products list
Market = {'1': ['shoes', 2000, 100],
          '3': ['Shirt', 1500, 200],
          '4': ['Jacket', 4000, 50],
          '5': ['T-Shirt', 2000, 70],
          }

clients = list(tuple())  # init clients list

balance = 0  # market balance


# generate sale cart
# frm client name
# number client number
# amount cart price
def getSaleCart(frm, number, amount):
    return f'''\
    
           {'{:-<60}'.format('-')}\n
           |{'{: <70}'.format('From : ' + frm + '    Nu: ' + str(number))}|\n
           |{'{: <70}'.format('To : ' + 'Tariq Mohammed')}|\n
           |{'{: <70}'.format('Amount : ' + str(amount) + '$')}|\n
           {'{:-<60}'.format('-')}\n

            Send 'K' To Accept OR 'C' To Cancel.
       \
'''


# set help string
helpString = '''\

 Notes:- 
    To Sell Enter 'S' Then Product Id Then Quantity Separated By space. such : 'S 1 3'.
    To Display Product List Enter 'P'.
    To Close Connection Enter 'X'.
    Enter 'H' To Redisplay This Notes.
\
'''


# style and return product table
def getProductList():
    markstr = 'Products list :-\n' + str('{:-^45}\n'.format('-') +
                                         '\n|{:^5}|{:^15}|{:^10}|{:^10}|'.format(
                                             'id',
                                             'Name',
                                             'Price',
                                             'Available') +
                                         '\n{:-^45}\n'.format('-'))
    for item in Market:
        markstr = markstr + '|{:^5}|{:^15}|{:^10}|{:^10}|\n'.format(item, Market[item][0], Market[item][1],
                                                                    Market[item][2])
    return markstr


# init server admin help message
adminHelp = '''\
server commands:
F turnOff server
O turnOn server
R print report
P get product list
H show help message
A add product
D delete product


\
'''


# confirm new connections
# con represent connection socket between server and client
def newClient(con: socket.socket):
    global serverTurnedOn
    try:
        con.setblocking(True)  # run in blocking mode to ignore errors
        con.send(
            'Welcome to Al-Sultan Market \n please send your cart number.'.encode())  # request client number to use it in sale Cart
        success = False
        nm = ''  # receive number from client
        # make fore tries for client to send valid number
        for i in range(1, 4):
            try:
                nm = con.recv(1024).decode().strip()  # receive number from client
                nm = socket.ntohl(int(nm))  # reformat number to host support
                success = True  # to refer that for loop ended with success connection
                clients.append((con, nm))  # add new client to client's list
                break
            except socket.error as e:  # when connection error occur break
                print(str(e))
                break
            except Exception as e:
                if i ==3:
                    con.send('Connection Ended.\n You try many times'.encode())
                else:
                    con.send(f'invalid please send again {3-i}'.encode())
        # if for ended with successful connection end connection
        if success:  # else start response to client requests
            global helpString, Market, balance
            con.send(
                str('Products list :-\n\n' + getProductList() + helpString ).encode())  # send product list and help message for first connection
            # save last Sale data
            lastSale = 0
            lastItem = '0'
            while serverTurnedOn:
                try:
                    con.settimeout(60 * 2)  # set timeout for each task 2 minutes
                    data = con.recv(1024).decode().strip().lower()  # receive From specific client
                    response = ''
                    if lastSale > 0:  # check last request is to sale

                        if data == 'k':  # check if client accept to payment for last sale
                            response = f'You Have Payment {Market[lastItem][1] * lastSale} Successfully\n'
                            balance += Market[lastItem][1] * lastSale  # add to server balance
                            Market[lastItem][2] -= lastSale  # decrease product quantity after sale
                        elif data == 'c':  # check if client cancel last sale
                            response = 'Your Last Sale Canceled\n'
                        else:  # other command not valid
                            response = 'Your Last Payment Canceled\n Invalid Commend'
                        # reset variables
                        lastSale = 0
                        lastItem = '0'
                    elif data == 'x':  # if client request end connection data well be 'x'
                        if clients.__contains__((con, nm)):  # check if clients list contain this client then remove it
                            clients.remove((con, nm))  # remove client from clients list
                        break
                    elif data == 'p':  # check if client request products list
                        response = getProductList()
                    elif data == 'h':  # check if client request help message
                        response = helpString

                    # check if request to sale
                    elif data.startswith('s'):  # check if request match sale command
                        req = data.split(' ')  # split the request to validate remaining parts of command
                        pid = req[1].strip()
                        qu = int(req[2].strip())
                        if Market.keys().__contains__(pid):  # check if product id exist
                            if Market[pid][2] >= qu:  # check if needed quantity available
                                totalPrice = Market[pid][1] * qu  # calculate total price
                                # save last sale data for processing next request
                                lastSale = qu  # save quantity
                                lastItem = pid  # save product id
                                response = getSaleCart(str(con.getpeername()), nm,
                                                       totalPrice)  # get sale cart to payment
                            else:  # needed quantity not available
                                response = f'Available Quantity {Market[pid][2]}.\nstart new command '
                        else:  # product id not exist
                            response = 'Product Id Not Exist.'
                    else:  # check for other request
                        response = 'Invalid Command Please Try Again'
                    con.send(response.encode())  # sent response
                except ConnectionError as e:
                    if clients.__contains__((con, nm)):  # check if clients list contain this client then remove it
                        clients.remove((con, nm))  # remove client from clients list
                    break
                except TimeoutError as e:
                    if clients.__contains__((con, nm)):
                        clients.remove((con, nm))
                    break
                except socket.error as e:
                    print(str(f'RCV SE {e}'))
                    if clients.__contains__((con, nm)):
                        clients.remove((con, nm))
                    break
                except Exception as e:
                    print(str(f'RCV E {str(e)}'))
                    con.send('command invalid'.encode())
        if not serverTurnedOn:
            con.send('Connection End.\n server has End Connection.'.encode())

        con.close()  # end connection

    except Exception as e:
        print(str(f'RCV E {e}'))


# init server socket and start serve customers
# server start in new thread to continue response admin commands in main thread
# when admin want close server the serverTurnedOn wel be False and the server socket wel close
def startServer():
    global serverTurnedOn
    try:
        # init server socket with IPv4 and TCP connection Protocol
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setblocking(True)  # to continue when some errors occur
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # to white if address and port are busy
        address = '127.0.0.1'  # get current host ip to bind
        serverSocket.bind(('', 5000))  # bind port and address
        serverTurnedOn = True
        print('server turned on.')  # notify admin when server ready to accept connections
        serverSocket.listen(5)  # start listen
        # while server on accept multi-connections
        while serverTurnedOn:
            try:
                serverSocket.settimeout(30)
                con, addr = serverSocket.accept()  # get new connection
                threading.Thread(target=newClient, args=(con,)).start()  # start serve client in new thread
            except TimeoutError as e:
                continue
            except Exception as e:
                print(str(e))
        serverTurnedOn = False
        serverSocket.close()  # close server socket
        print('server turned of')  # notify admin when server has closed
    except Exception as e:
        serverTurnedOn = False
        print(f'start server error {e}')  # print errors when cached


if __name__ == '__main__':
    print(adminHelp)
    try:
        # for this code see 'adminHelp' variable to know why conditions
        while True:
            try:
                inp = input('enter your command \n')
                inp = inp.strip().lower()
                if inp == 'f':  # if command refer to turn server off
                    if not serverTurnedOn:
                        print('server not running')
                    else:
                        serverTurnedOn = False
                elif inp == 'o':  # if command refer to turn server on
                    # check server if it already runs notify admin and not run new thread
                    if serverTurnedOn:
                        print('server is running')
                        continue  # continue while loop and not perform other statements
                    threading.Thread(target=startServer).start()  # start server in new thread
                elif inp == 'r':  # if command refer to print inf :customers number and balance
                    print(F'customers :{len(clients)}\nbalance : {balance}\n')

                elif inp == 'p':  # if command refer to print products list
                    print(getProductList())

                elif inp == 'h':  # if command refer to print admin help message
                    print(adminHelp)

                elif inp == 'a':  # if command refer to add new product
                    type = input('Enter \'N\' To Add New or other letter to Edit Existing product>>')
                    if type.strip().lower() == 'n':
                        details = input('enter Name then comma and price,then comma and quantity >> ')
                        details = details.strip().split(',')
                        # to generate new id for new product
                        id = len(Market.keys())
                        while Market.keys().__contains__(str(id)):  # while id exist
                            id += 1
                        Market[str(id)] = [details[0].strip(), int(details[1].strip()), int(details[2].strip())]
                    else:
                        details = input('enter product id then comma and new price then comma and new quantity >> ')
                        details = details.strip().split(',')
                        if not Market.keys().__contains__(details[0].strip()):
                            print('sorry these id not exist')
                            continue
                        Market[details[0].strip()][1] = int(details[1].strip())  # set new price
                        Market[details[0].strip()][2] = int(details[2].strip())  # set new quantity
                elif inp == 'd':  # if command refer to delete product from list
                    id = input('enter product id >>')  # get product id
                    if Market.keys().__contains__(id):  # if id exist delete it
                        Market.pop(id)
            except Exception as e:
                print(f'{e} Invalid Command please try again')
    except KeyboardInterrupt as e:
        print('shutdown!')
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
