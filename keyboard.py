from backend import *

def keyboard():
    global stop_event
    wish()
    speak("How can I help you, Sir?")
    
      # Set a timeout to prevent blocking
    
    while not stop_event.is_set():  # Add a stop condition to control the infinite loop
        try:
            query = client_socket.recv(1024)
            if not query:  # Client disconnected or no data received
                continue
            query = query.decode('utf-8')  # Decode the byte object to string

            if query.lower() == "none":
                continue
        finally:
            query = ap.processcmd(query)
            command, param = process_airesponse(query)
        
        if command is None and param is None:
            default_fucntion(query)

        try:
            if command:
                action = command_actions.get(command)
                if param:
                    action(param)  # If there is a parameter, pass it to the function
                else:
                    action()
        except Exception as e:
            printBubble(e)
        time.sleep(5)
        speak("Sir, Do you have any other work")
keyboard()