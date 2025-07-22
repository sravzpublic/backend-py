# https://pennies.interactivebrokers.com/cstools/contract_info/v3.10/index.php
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

    def handler(self, signum, frame):
        # print("Signal received! exiting!")
        if self.isConnected():
            self.disconnect()

def main():
    app = TestApp()
    setup.set_signal_handler(app.disconnect)
    app.connect(settings.constants.IBKR_API_HOSTNAME, 
                settings.constants.IBKR_API_PORT, 
                settings.constants.IBKR_API_CLIEND_ID)

    mycontract = Contract()
    # All details
    mycontract.symbol = "NQ"
    mycontract.secType = "FOP"
    mycontract.exchange = "CME"
    mycontract.currency = "USD"
    mycontract.right = "C"
    # Get all call options by not specifying below properties
    mycontract.lastTradeDateOrContractMonth = "20231108"
    # mycontract.strike = 15500

    # Using contract ID
    # mycontract.conId = 663893270
    # Sleep until IBKR API connection is complete
    # while not app.isConnected():
    time.sleep(3)

    app.reqContractDetails(1, mycontract)

    app.run()

if __name__ == "__main__":
    main()
