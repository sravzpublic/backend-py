from src.ibkr.tests import setup
from src.util import settings
from ibapi.client import *
from ibapi.wrapper import *
from ibapi.tag_value import *

class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId: int):
        sub = ScannerSubscription()
        sub.instrument = "FUT.US"
        sub.locationCode = "FUT.US"
        sub.scanCode = "MOST_ACTIVE_USD"

        scan_options = []
        filter_options = [
            # TagValue("volumeAbove","10000"),
            # TagValue("marketCapBelow1e6", "1000"),
            # TagValue("priceAbove", '1')
        ]

        self.reqScannerSubscription(orderId, sub, scan_options, filter_options)

    def scannerData(self, reqId, rank, contractDetails, distance, benchmark, projection, legsStr):
        print(f"scannerData. reqId: {reqId}, rank: {rank}, contractDetails: {contractDetails}, distance: {distance}, benchmark: {benchmark}, projection: {projection}, legsStr: {legsStr}.")

    def scannerDataEnd(self, reqId):
        print("ScannerDataEnd!")
        self.cancelScannerSubscription(reqId)
        self.disconnect()


app = TestApp()
app.connect(settings.constants.IBKR_API_HOSTNAME, 
            settings.constants.IBKR_API_PORT, 
            settings.constants.IBKR_API_CLIEND_ID)
setup.set_signal_handler(app.disconnect)
app.run()