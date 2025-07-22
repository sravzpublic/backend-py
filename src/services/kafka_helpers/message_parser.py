import msgpack, json
from src.analytics import stats
from src.services.cache import Cache
from .message_contracts import MessageContracts

class MessageParser(object):
    """
        Parse Sravz Message and hendle the message
    """
    def __init__ (self):
        """
        """
        super(MessageParser, self).__init__()

    def parse (self, msg):
        """
            Contains incoming message from Kafka
        """
        pass

    def get_input_message (self, msg_in):
        """
            Perform decoding and understand the message
            # Message format
            {
                #Message identifier
                id: number
                #Input params
                p_i:
                #Topic on which to send output data
                t_o:
                #Output data
                d_o:
            }
        """
        if msg_in:
            return MessageContracts.get_input_message(msg_in)
        return None


    def get_output_message (self, msg):
        """
            Perform enconding and create the response message
        """
        if msg:
            return MessageContracts.get_output_message(msg)
        return None
        #return msgpack.unpackb(eng.get_historical_rolling_stats(msg))

