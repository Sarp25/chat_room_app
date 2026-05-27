import socket, threading, sys, os, time

if os.name== 'nt':
    os.system('')

nickname= input("Choose your nickname: ")
if not nickname.strip():
    print("Nickname cannot be empty.")
    sys.exit()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect(('127.0.0.1', 55555))
except Exception as e:
    print(f"\033[31mCould not connect to server: {e}\033[0m")
    sys.exit()

try:
    first_msg= client.recv(1024).decode('utf-8')
    if first_msg== 'NICK':
        client.send(nickname.encode('utf-8'))
        
        response= client.recv(1024).decode('utf-8')
        if "Disconnecting" in response or "invalid" in response:
            print(response)
            client.close()
            sys.exit()
        else:
            print(response)
except Exception as e:
    print(f"\033[31mHandshake failed: {e}\033[0m")
    client.close()
    sys.exit()

running= True
waiting_for_input= False

def receive():
    global running, waiting_for_input
    while running:
        try:
            message= client.recv(1024).decode('utf-8')
            if not message:
                break
                
            if waiting_for_input:
                sys.stdout.write(f"\r\033[K{message}\n> ")
            else:
                sys.stdout.write(f"{message}\n")
                
            sys.stdout.flush()
        except:
            print("\n\033[31m[SYSTEM] Connection to server lost.\033[0m")
            running= False
            break

def write():
    global running, waiting_for_input
    while running:
        try:
            waiting_for_input= True
            user_input= input("> ")
            waiting_for_input= False
            
            if not user_input.strip():
                continue
                
            client.send(user_input.encode('utf-8'))
            
            
            time.sleep(0.05)
        except (KeyboardInterrupt, EOFError):
            running=False
            break
        except:
            break


receive_thread=threading.Thread(target=receive)
receive_thread.daemon=True
receive_thread.start()

write_thread=threading.Thread(target=write)
write_thread.daemon=True
write_thread.start()

try:
    while running:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nExiting chat application...")
finally:
    running=False
    client.close()
    sys.exit()