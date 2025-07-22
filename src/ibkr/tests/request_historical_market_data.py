from src.ibkr.tests import setup
from src.util import settings
from ibapi.client import *
from ibapi.wrapper import *

class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId: int):
        
        mycontract = Contract()
        # mycontract.symbol = "AAPL"
        # mycontract.secType = "STK"
        # mycontract.exchange = "SMART"
        # mycontract.currency = "USD"

        mycontract.symbol = "NQ"
        mycontract.secType = "FOP"
        mycontract.exchange = "CME"
        mycontract.currency = "USD"
        mycontract.right = "C"
        # Get all call options by not specifying below properties
        mycontract.lastTradeDateOrContractMonth = "20231110"
        mycontract.strike = 14000

        self.reqHistoricalData(orderId, mycontract, "15:59:00", "1 D", "1 hour", "TRADES", 0, 1, 0, [])

    def historicalData(self, reqId, bar):
        print(f"Historical Data: {bar}")

    def historicalDataEnd(self, reqId, start, end):
        print(f"End of HistoricalData")
        print(f"Start: {start}, End: {end}")


app = TestApp()
app.connect(settings.constants.IBKR_API_HOSTNAME, 
            settings.constants.IBKR_API_PORT, 
            settings.constants.IBKR_API_CLIEND_ID)
setup.set_signal_handler(app.disconnect)
app.run()