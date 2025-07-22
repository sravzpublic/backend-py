from src.ibkr.tests import setup
from src.util import settings
from ibapi.client import *
from ibapi.wrapper import *
import time

class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)
        self.mycontract = None
        self.orderId = None
        self.strike_prices = [14170] #, 14175, 14180] #, 14190, 14200, 14210, 14220, 14225, 14230, 14240, 14250, 14260, 14270, 14275, 14280, 14290, 14300, 14310, 14320, 14325, 14330, 14340, 14350, 14360, 14370, 14375, 14380, 14390, 14400, 14410, 14420, 14425, 14430, 14440, 14450, 14460, 14470, 14475, 14480, 14490, 14500, 14510, 14520, 14525, 14530, 14540, 14550, 14560, 14570, 14575, 14580, 14590, 14600, 14610, 14620, 14625, 14630, 14640, 14650, 14660, 14670, 14675, 14680, 14690, 14700, 14710, 14720, 14725, 14730, 14740, 14750, 14760, 14770, 14775, 14780, 14790, 14800, 14810, 14820, 14825, 14830, 14840, 14850, 14860, 14870, 14875, 14880, 14890, 14900, 14910, 14920, 14925, 14930, 14940, 14950, 14960, 14970, 14975, 14980, 14990, 15000, 15010, 15020, 15025, 15030, 15040, 15050, 15060, 15070, 15075, 15080, 15090, 15100, 15110, 15120, 15125, 15130, 15140, 15150, 15160, 15170, 15175, 15180, 15190, 15200, 15210, 15220, 15225, 15230, 15240, 15250, 15260, 15270, 15275, 15280, 15290, 15300, 15310, 15320, 15325, 15330, 15340, 15350, 15360, 15370, 15375, 15380, 15390, 15400, 15410, 15420, 15425, 15430, 15440, 15450, 15460, 15470, 15475, 15480, 15490, 15500, 15510, 15520, 15525, 15530, 15540, 15550, 15560, 15570, 15575, 15580, 15590, 15600, 15625, 15650, 15675, 15700, 15725, 15750, 15800, 15850, 15900, 15950, 16000, 16050, 16100, 16200, 16250, 16300, 16400, 16500, 16750, 17000, 17250, 17500, 17750, 18000, 18500, 19000, 19500, 20000, 20500, 21000]
        self.curent_strike_price_index = 0
        self.total_strikes = len(self.strike_prices)

    def get_next_strike_price(self):
        strike_price = None
        if self.curent_strike_price_index < self.total_strikes:
            strike_price = self.strike_prices[self.curent_strike_price_index]
            self.curent_strike_price_index =self.curent_strike_price_index + 1
        return strike_price
        
    def nextValidId(self, orderId: int):        
        self.mycontract = Contract()
        # mycontract.symbol = "AAPL"
        # mycontract.secType = "STK"
        # mycontract.exchange = "SMART"
        # mycontract.currency = "USD"

        self.mycontract.symbol = "NQ"
        self.mycontract.secType = "FOP"
        self.mycontract.exchange = "CME"
        self.mycontract.currency = "USD"
        self.mycontract.right = "C"
        # Get all call options by not specifying below properties        
        self.mycontract.lastTradeDateOrContractMonth = "20231108"        
        self.reqMarketDataType(4)

        # for strike_price in strike_prices:
        strike_price = self.get_next_strike_price()
        if strike_price:
            print(f"Requesting price for strike: {strike_price} - orderID: {orderId}")
            self.mycontract.strike = strike_price
            self.reqMktData(strike_price, self.mycontract, "", 0, 0, [])
            self.orderId = orderId


    def tickPrice(self, reqId, tickType, price, attrib):
        print(f"tickPrice. reqId: {reqId}, tickType: {TickTypeEnum.to_str(tickType)}, price: {price}, attribs: {attrib}")
        self.cancelMktData(reqId)
        # strike_price = self.get_next_strike_price()
        # if strike_price:
        #     self.mycontract.strike = strike_price
        #     self.orderId = self.orderId+1
        #     self.reqMktData(self.orderId, self.mycontract, "", 0, 0, [])

    def tickSize(self, reqId, tickType, size):
        print(f"tickSize. reqId: {reqId}, tickType: {TickTypeEnum.to_str(tickType)}, size: {size}")
        self.cancelMktData(reqId)
        

app = TestApp()
app.connect(settings.constants.IBKR_API_HOSTNAME, 
            settings.constants.IBKR_API_PORT, 
            settings.constants.IBKR_API_CLIEND_ID)
setup.set_signal_handler(app.disconnect)
app.run()