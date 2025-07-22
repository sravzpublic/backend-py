import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
import signal

def set_signal_handler(handler):    
    def _handler(signum, frame):        
        print("Signal handler called")
        handler()
        print("Signal handler finished")
    signal.signal(signal.SIGINT, _handler)
