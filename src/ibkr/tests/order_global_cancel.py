from src.ibkr.tests import setup
from ibapi.client import *
from ibapi.wrapper import *
from src.util import settings

class TestApp(EClient, EWrapper):
  def __init__(self):
    EClient.__init__(self, self)

  def nextValidId(self, orderId: OrderId):
    self.reqGlobalCancel()

app = TestApp()
app.connect(settings.constants.IBKR_API_HOSTNAME, 
            settings.constants.IBKR_API_PORT, 
            settings.constants.IBKR_API_CLIEND_ID)
setup.set_signal_handler(app.disconnect)
print(f"Connecting to client as clientID: {settings.constants.IBKR_API_CLIEND_ID}")
app.run()