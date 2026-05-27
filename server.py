import socket, threading, time

HOST = "127.0.0.1"  # Localhost for testing
PORT = 55555        # Updated to 55555 to sync cleanly with the new client.py


RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"

lock= threading.Lock()
clients= []
nicknames= []

server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Prevents "Address already in use" errors
server.bind((HOST, PORT))
server.listen()

def broadcast(message, exclude_client=None):
    with lock:
        current_clients= list(clients)
    
    for client in current_clients:
        if client== exclude_client:
            continue
        try:
            client.send(message)
        except:
            remove_client(client)

def remove_client(client):
    with lock:
        if client in clients:
            index= clients.index(client)
            clients.remove(client)
            client.close()
            nickname=nicknames[index]
            nicknames.remove(nickname)
            
            disconnect_msg= f"{RED}[SYSTEM] {nickname} left the chat!{RESET}"
            print(f"[-] {nickname} disconnected.")
            
            threading.Thread(target=broadcast, args=(disconnect_msg.encode('utf-8'),)).start()

def handle_client(client, nickname):
    while True:
        try:
            message= client.recv(1024)
            if not message:
                break
            
            actual_content= message.decode('utf-8').strip()

            if actual_content== '/help':
                help_text= (
                    f"\n{YELLOW}--- All Commands ---\n"
                    f"/list                   - Show all online users\n"
                    f"/msg [username] [msg]   - Send a private message\n"
                    f"/help                   - Show this menu{RESET}\n"
                )
                client.send(help_text.encode('utf-8'))

            elif actual_content.startswith('/msg '):
                parts= actual_content.split(' ', 2)
                if len(parts) >=3:
                    target_nickname= parts[1]
                    private_text= parts[2]
                    
                    with lock:
                        if target_nickname in nicknames:
                            target_index= nicknames.index(target_nickname)
                            target_client= clients[target_index]
                            found= True
                        else:
                            found= False
                            
                    if found:
                        formatted_pm_recipient= f"{CYAN}[PM from {nickname}]: {private_text}{RESET}"
                        formatted_pm_sender= f"{CYAN}[PM to {target_nickname}]: {private_text}{RESET}"
                        
                        target_client.send(formatted_pm_recipient.encode('utf-8'))
                        client.send(formatted_pm_sender.encode('utf-8'))
                    else:
                        client.send(f"{RED}Server: User '{target_nickname}' not found.{RESET}".encode('utf-8'))
                else:
                    client.send(f"{RED}Server: Invalid format. Use /msg username message{RESET}".encode('utf-8'))
            
            elif actual_content== '/list':
                with lock:
                    online_users= ", ".join(nicknames)
                client.send(f"{MAGENTA}Server: Online users ({len(nicknames)}): {online_users}{RESET}".encode('utf-8'))

            else:
                colored_message= f"{GREEN}{nickname}{RESET}: {actual_content}"
                broadcast(colored_message.encode('utf-8'), exclude_client=client)
                
        except:
            break
    remove_client(client)

def receive():
    server.settimeout(1.0)

    print(f"Server is running and listening on {HOST}:{PORT}...")
    while True:
        try:
            client, address= server.accept()
            print(f"[+] Connected with {str(address)}")

            client.send('NICK'.encode('utf-8'))
            nickname= client.recv(1024).decode('utf-8').strip()
            
            with lock:
                if nickname in nicknames or not nickname:
                    client.send(f"{RED}Server: Nickname invalid or taken. Disconnecting.{RESET}".encode('utf-8'))
                    time.sleep(0.1) # Buffer cooldown to ensure delivery before closing
                    client.close()
                    continue
                
                nicknames.append(nickname)
                clients.append(client)

            print(f"Nickname of the client is {nickname}!")
            
            join_msg= f"{YELLOW}[SYSTEM] {nickname} joined the chat!{RESET}"
            broadcast(join_msg.encode('utf-8'), exclude_client=client)
            
            welcome_msg= (
                f"{YELLOW}Connected to the server successfully!\n"
                f"[SYSTEM] Type /help to see available commands.{RESET}"
            )
            client.send(welcome_msg.encode('utf-8'))

            thread= threading.Thread(target=handle_client, args=(client, nickname))
            thread.start()

        except socket.timeout:
            continue   


if __name__ == "__main__":
    try:
        receive()
    except KeyboardInterrupt:
        print("\nShutting down server...")