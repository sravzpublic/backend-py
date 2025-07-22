from src.ibkr.tests import setup
from ibapi.client import *
from ibapi.wrapper import *
import time
from src.util import settings

# ESClient Outgoing Messages. EWrapper Incoming Messages.
class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)

    def contractDetails(self, reqId, contractDetails):
        print(f"contract details: {contractDetails}")
        # pprint.pprint(contractDetails, depth=1)

    def contractDetailsEnd(self, reqId):
        print("End of contractDetails")
        self.disconnect()

def main():
    app = TestApp()
    setup.set_signal_handler(app.disconnect)
    app.connect(settings.constants.IBKR_API_HOSTNAME, 
                settings.constants.IBKR_API_PORT, 
                settings.constants.IBKR_API_CLIEND_ID)
    mycontract = Contract()
    mycontract.symbol = "AAPL"
    mycontract.secType = "STK"
    # IBKR smart routing - exchange SMART
    mycontract.exchange = "SMART" 
    mycontract.currency = "USD"
    # NASDAQ is also referred to as ISLAND
    mycontract.primaryExchange = "ISLAND"

    # Sleep until IBKR API connection is complete
    # while not app.isConnected():
    time.sleep(3)

    app.reqContractDetails(1, mycontract)

    app.run()

if __name__ == "__main__":
    main()