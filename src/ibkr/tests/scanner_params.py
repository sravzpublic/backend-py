from src.ibkr.tests import setup, util
from src.util import settings
from ibapi.client import *
from ibapi.wrapper import *

class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId: int):
        self.reqScannerParameters()

    def scannerParameters(self, xml):
        open(settings.constants.IBKR_SCANNER_PARAMS_XML_FILE_PATH, 'w').write(xml)
        print("Scanner parameters received!")
        util.save_xml_to_json(settings.constants.IBKR_SCANNER_PARAMS_XML_FILE_PATH, 
                              settings.constants.IBKR_SCANNER_PARAMS_JSON_FILE_PATH)

app = TestApp()
app.connect(settings.constants.IBKR_API_HOSTNAME, 
            settings.constants.IBKR_API_PORT, 
            settings.constants.IBKR_API_CLIEND_ID)
setup.set_signal_handler(app.disconnect)
app.run()