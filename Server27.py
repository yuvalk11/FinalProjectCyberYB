import select
import socket


import pyodbc
class Server27:
    def __init__(self,IP,port):
        self.port=port
        self.IP =IP

    def receive_client_request(self,client_socket):
        """Receives the full message sent by the clientTAKE

        Works with the protocol defined in the client's "send_request_to_server" function

        Returns:
            command: such as DIR, EXIT, SCREENSHOT etc
            params: the parameters of the command

        Example: 12DIR c:\cyber as input will result in command = 'DIR', params = 'c:\cyber'
        """

        length = client_socket.recv(4).decode()
        message = client_socket.recv(int(length)).decode()

        messagelist = message.split("#")
        command = messagelist[0]
        info = messagelist[1]
        return command,info

    def handle_client_request(self,command, params, client_socket):
        """Create the response to the client, given the command is legal and params are OK

        For example, return the list of filenames in a directory

        Returns:
            response: the requested data
        """

        connString = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-DV5FBQ6;PORT=1433;DATABASE=stepAhead;UID=YUVAL;PWD=YUVALPassword12'
        print(connString)

        try:
            cn = pyodbc.connect(connString)
            print('You are connected to db ')


        except Exception as e:
            print('Error connecting to databse: ', str(e))

        queryUser = params;
        cursor = cn.cursor()
        message1 = ''

        if command == "select":
            cursor.execute(queryUser)
            for i in cursor:
                message1 += str(i) + '#'


        elif command == "insert":
            cursor.execute(queryUser)
            cn.commit()
            message1 = 'done'

        elif command== "update":
            cursor.execute(queryUser)
            cn.commit()
            message1 = 'done'


        cn.close()
        print('Connection closed')
        return message1

    def send_response_to_client(self,response, client_socket):
        """Create a protocol which sends the response to the client

        The protocol should be able to handle short responses as well as files
        (for example when needed to send the screenshot to the client)
        print
        """
        print(response)
        message =  response + "\n"
        client_socket.send(message.encode())
        print(response)

    def method_send(self,current_socket, send, messages_to_send, wlist):
        for message in messages_to_send:
            current_socket, send = message
            if current_socket in wlist:
                self.send_response_to_client(send, current_socket)
                messages_to_send.remove(message)

        return messages_to_send, wlist

    def print_client_sockets(self,client_sockets):
        for c in client_sockets:
            print("\t", c.getpeername())

    def execute_server(self):
        print("Setting up server...")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.IP, self.port))
        server_socket.listen()
        print("Listening for clients...")
        client_sockets = []
        messages_to_send = []

        while True:
            rlist, wlist, xlist = select.select([server_socket] + client_sockets, client_sockets, [])
            for current_socket in rlist:
                if current_socket is server_socket:
                    connection, client_address = current_socket.accept()
                    print("New client joined!", client_address)
                    client_sockets.append(connection)
                    self.print_client_sockets(client_sockets)

                else:
                    done = False
                    while not done:
                        command, params = self.receive_client_request(current_socket)
                        print(command)
                        print(params)

                        response = self.handle_client_request(command, params, current_socket)
                        messages_to_send.append((current_socket, response))  ###
                        messages_to_send, wlist = self.method_send(current_socket, response, messages_to_send, wlist)
                        done=True





                    if done:
                        print("Connection closed1")
                        client_sockets.remove(current_socket)
                        current_socket.close()
                        self.print_client_sockets(client_sockets)
def main():
    server=Server27("0.0.0.0",6969)
    server.execute_server()

if __name__ == '__main__':
    main()