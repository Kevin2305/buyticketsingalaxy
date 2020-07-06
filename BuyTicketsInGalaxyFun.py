#!/usr/bin/env python
# coding: utf-8
import configparser
import base64,json
from requests import post,exceptions as postexcept
import logging,sys,os
from datetime import datetime
import xmltodict
from BuyTicketsInGalaxyClass import *
mylogger=logging.getLogger("buyticketingalaxy")
messageid = 0
url_qa = "https://shtktefg-qa.shdrapps.disney.com"
url_dev = "https://shtktefg-dev.shdrapps.disney.com"
url_lt = "https://shtktefg-lt.shdrapps.disney.com"
env = 'dev'

def InitLogger():
    if os.path.exists("config.txt"):
        cp = configparser.ConfigParser()
        cp.read("./config.txt")
        looglevel = cp.get('config','loglevel')
        if looglevel == 'warn':
            loglevel = logging.WARN
        if looglevel == 'error':
            loglevel = logging.ERROR
        if looglevel == 'info':
            loglevel = logging.INFO
        if looglevel == 'debug':
            loglevel = logging.DEBUG
        else:
            loglevel = logging.WARN
    else:
        loglevel = logging.DEBUG
    global mylogger
    #loglevel = logging.WARN
    handler1 = logging.StreamHandler()
    handler2 = logging.FileHandler(filename='buyticketingalaxy.log',encoding="utf-8",delay=False)
    mylogger.setLevel(logging.DEBUG)
    handler1.setLevel(logging.DEBUG)
    handler2.setLevel(loglevel)
    datefmt="%Y-%m-%d %H:%M:%S"
    fmt="%(asctime)s %(name)s %(levelname)s : %(message)s"
    logfmt = logging.Formatter(fmt=fmt,datefmt=datefmt)
    handler1.setFormatter(logfmt)
    handler2.setFormatter(logfmt)
    mylogger.addHandler(handler1)
    mylogger.addHandler(handler2)
    mylogger.info("Event Log Started")

def getMessageID():
    global messageid
    messageid = messageid + 1
    return str(messageid)

def authenticate_1(username,password):
    cmd = """
    <Envelope 
    xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <Header>
    <SourceID>GAL</SourceID>
    <MessageID>$messageid$</MessageID>
    <MessageType>Authenticate</MessageType>
    <TimeStamp>$timestamp$</TimeStamp>
    <EchoData/>
    <SystemFields/>
    </Header>
    <Body>
    <Authenticate>
    <Username>$username_galaxy$</Username>
    <Password>$password_galaxy$</Password>
    <PasswordEncrypted>NO</PasswordEncrypted>
    </Authenticate>
    </Body>
    </Envelope>
    """
    cmd = cmd.replace("$messageid$",getMessageID())
    cmd = cmd.replace("$timestamp$",getTimeStamp())
    cmd = cmd.replace("$username_galaxy$",username)
    cmd = cmd.replace("$password_galaxy$",password)
    mylogger.debug("authenticate request: " + cmd)
    response = post2eGalaxy(env,cmd)
    if response:
        return xml2Dict(response)['Envelope']['Body']['AuthenticateResponse']['SessionID']
    return None

def holdEvent_2(pt):
    cmd = """
    <Envelope 
    xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <Header>
    <SourceID>GAL</SourceID>
    <MessageID>2</MessageID>
    <MessageType>EventTicketHold</MessageType>
    <SessionID>36607240</SessionID>
    <TimeStamp>2020-07-03 09:37:53</TimeStamp>
    <EchoData/>
    <SystemFields/>
    </Header>
    <Body>
    <EventTicketHold>
    <EventID>26738</EventID>
    <SectionID>1</SectionID>
    <Qty>1</Qty>
    <PLU>SHTP01WSRET1806SS</PLU>
    </EventTicketHold>
    </Body>
    </Envelope>
    """


def confirmOrder_3(dd):
    orderline = """

    """
    cmd = """
    <Envelope
    	xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    	<Header>
    		<SourceID>GAL</SourceID>
    		<MessageID>1</MessageID>
    		<MessageType>Orders</MessageType>
    		<TimeStamp>2020-07-03 09:48:16</TimeStamp>
    		<EchoData/>
    		<SystemFields/>
    	</Header>
    	<Body>
    		<Orders>
    			<Order>
    				<OrderID>GAL000322006554677</OrderID>
    				<OrderCommand>Add</OrderCommand>
    				<SessionID>36607477</SessionID>
    				<CustomerID>3046</CustomerID>
    				<OrderDate>2020-07-03 09:48</OrderDate>
    				<OrderTotal>913.00</OrderTotal>
    				<OrderStatus>2</OrderStatus>
    				<OrderContact>
    					<Contact>
    						<FirstName>Tianjin XiGua Travel Co., Ltd</FirstName>
    						<LastName>Tianjin XiGua Travel Co., Ltd</LastName>
    						<Email>tradeclient@tradeclient.com</Email>
    						<IdentificationNo>612323199001302914</IdentificationNo>
    					</Contact>
    				</OrderContact>
    				<GroupVisit>
    					<VisitDate>2020-07-03</VisitDate>
    				</GroupVisit>
    				<Shipping>
    					<DeliveryMethod>11</DeliveryMethod>
    					<DeliveryDetails>Galasys</DeliveryDetails>
    				</Shipping>
    				<OrderLines>$ticketsorderlines$
                    <OrderLine>
    						<DetailType>2</DetailType>
    						<Description>63</Description>
    						<Qty>0</Qty>
    						<Amount>913.00</Amount>
    						<Total>913.00</Total>
    						<PaymentCode>63</PaymentCode>
    						<PaymentDate>2020-07-03 09:48:16</PaymentDate>
    						<Endorsement>XXXXXXXXXXXXXXX7636</Endorsement>
    					</OrderLine>
    				</OrderLines>
    				<UserFields>
    					<UserField2>YES/是</UserField2>
    					<UserField3>GALASYS_API</UserField3>
    				</UserFields>
    			</Order>
    		</Orders>
    	</Body>
    </Envelope>
    """
    
def updateGovID(galorderid,newid):
    cmd = """
    <Envelope
	xmlns:xsd="http://www.w3.org/2001/XMLSchema"
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
	<Header>
		<SourceID>GAL</SourceID>
		<MessageID>1</MessageID>
		<MessageType>Orders</MessageType>
		<TimeStamp>$timestamp$</TimeStamp>
		<EchoData/>
		<SystemFields/>
	</Header>
	<Body>
		<Orders>
			<Order>
				<OrderID>$orderid$</OrderID>
				<OrderCommand>UpdateHeader</OrderCommand>
				<OrderContact>
					<Contact>
						<IdentificationNo>$govid$</IdentificationNo>
					</Contact>
				</OrderContact>
			</Order>
		</Orders>
	</Body>
    </Envelope>    
    """
    cmd = cmd.replace("$timestamp$",galorderid)
    cmd = cmd.replace("$orderid$",galorderid)
    cmd = cmd.replace("$govid$",newid)
    

def xml2Dict(xml):
    return xmltodict.parse(xml,encoding='utf-8')

def queryEventID(startd,endd,eventtype):
    cmd = """
    <?xml version="1.0" encoding="UTF-8"?>
    <Envelope>
    <Header>
    <SourceID>SHDR</SourceID>
    <MessageID>1</MessageID>
    <MessageType>QueryEvents</MessageType>
    <TimeStamp>2020-04-18 10:01:37</TimeStamp>
    </Header>
    <Body>
      <QueryEvents>
         <EventRangeBeginDate>2020-07-01 00:00:00</EventRangeBeginDate>
         <EventRangeEndDate>2020-08-30 23:59:59</EventRangeEndDate>
         <EventTypeID>27</EventTypeID>
         <PLU>SHFPBUNDA3B</PLU>
      </QueryEvents>
    </Body>
    </Envelope>
    """

def queryItems(customerid):
    cmd = """
    <Envelope 
    xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    	<Header>
    		<SourceID>GAL</SourceID>
    		<MessageID>$messageid$</MessageID>
    		<MessageType>QueryCustomerItems</MessageType>
    		<TimeStamp>$timestamp$</TimeStamp>
    	</Header>
    	<Body>
    		<QueryCustomerItems>
    			<CustomerID>$customerid$</CustomerID>
                <UseSalesProgramPricing>YES</UseSalesProgramPricing>
    		</QueryCustomerItems>
    	</Body>
    </Envelope>
    """
    cmd = cmd.replace("$messageid$",getMessageID())
    cmd = cmd.replace("$timestamp$",getTimeStamp())
    cmd = cmd.replace("$customerid$",customerid)
    response = post2eGalaxy(env,cmd)
    if response:
        ret_data = xml2Dict(response)['Envelope']['Body']['ItemList']
        if ret_data:
            items = []
            for item in ret_data['Item']:
                t_item = None
                t_item = Item( item['PLU'] , item['Name'] , item['Description'] , item['Price'] , item['EventTypeID'] , item['EventID'] , item['SectionID'] , item['Kind'] , None)
                if item.get('PackageDetails'):
                    for package in item['PackageDetails']['PackageDetail']:
                        t_item.addPackageDetails( Item( package['PLU'] , package['Name'] , package['Description'] , package['Price'] , package['EventTypeID'] , package['EventID'] , package['SectionID'] , package['Kind'] , None ) )
                items.append(t_item)
            return items
        else:
            mylogger.warning("queryItems no items in response")
    else:
        mylogger.warning("queryItems error in response")


def getTimeStamp():
    return datetime.today().strftime("%Y-%m-%d %H:%M:%S")

def post2eGalaxy(env,xmlrequest):
    if env == 'qa':
        url = url_qa
    if env == 'dev':
        url = url_dev
    if env == 'lt':
        url = url_lt
    mylogger.debug("request: " + xmlrequest)
    try:
        ret = post(url=url,data=xmlrequest,headers={'Content-Type':'application/xml','charset':'utf-8'},timeout=60)
        mylogger.debug("response: " + ret.content.decode('utf-8'))
        if ret.status_code == 200:
            return ret.content.decode('utf-8')
        return None
    except postexcept.HTTPError as e:
        mylogger.error("call eGalaxy error: " + str(e))
        return None


if __name__ == "__main__":
    InitLogger()
    username_galaxy = "RZME" #7104
    password_galaxy = "Disney001"
    env = 'dev'
    #items = queryItems('170')
    #for item in items:
    #    print(item.toStringBrief())
    sessionid = authenticate_1(username_galaxy,password_galaxy)