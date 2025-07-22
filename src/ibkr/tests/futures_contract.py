from src.ibkr.tests import setup
from ibapi.client import *
from ibapi.wrapper import *
import time
from src.util import settings

class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)

    def contractDetails(self, reqId, contractDetails):
        print(f"contract details: {contractDetails}")

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
    mycontract.symbol = "GC"
    mycontract.secType = "FUT"
    mycontract.exchange = "COMEX"
    mycontract.currency = "USD"
    # mycontract.lastTradeDateOrContractMonth = "202312"
    #mycontract.multiplier = 1

    # Or you can use just the Contract ID
    # mycontract.conId = 552142063

    # Sleep until IBKR API connection is complete
    #while not app.isConnected():
    time.sleep(3)

    app.reqContractDetails(1, mycontract)

    app.run()

if __name__ == "__main__":
    main()