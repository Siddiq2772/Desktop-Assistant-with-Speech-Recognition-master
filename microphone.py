import time
from backend import default_fucntion, printBubble, process_airesponse, speak, takecmd, wish, command_actions,ap

def microphone():
    global stop_event
    
    wish()
    speak("How can I help you, Sir?")
    
    while True:  # Add a stop condition to control the infinite loop
        query = takecmd().lower()
        user_query = query
        
        if query == "none":
            continue
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

microphone()