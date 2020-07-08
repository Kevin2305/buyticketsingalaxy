#!/usr/bin/env python
# coding: utf-8
import configparser
import base64,json
from requests import post,exceptions as postexcept
import logging,sys,os
from datetime import datetime,timedelta
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

def showENV():
    mylogger.info("ENV: " + env)

def getNextMessageID():
    global messageid
    messageid = messageid + 1
    return str(messageid)

def getCurrMessageID():
    global messageid
    return str(messageid)  

def authenticate_1(username,password,messageid):
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
    cmd = cmd.replace("$messageid$",messageid)
    cmd = cmd.replace("$timestamp$",getTimeStamp())
    cmd = cmd.replace("$username_galaxy$",username)
    cmd = cmd.replace("$password_galaxy$",password)
    response = post2eGalaxy(env,cmd)
    if response:
        body = xml2Dict(response)['Envelope']['Body']
        if body.get('AuthenticateResponse'):
            return 1,body['AuthenticateResponse']['SessionID']
        elif body.get('Error'):
            return 0,body['Error']['ErrorText']
    return 0,None

def EventTicketHold_2(messageid,sessionid,eventid,qty,item,sectionid):
    cmd = """
    <Envelope 
    xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <Header>
    <SourceID>GAL</SourceID>
    <MessageID>$messageid$</MessageID>
    <MessageType>EventTicketHold</MessageType>
    <SessionID>$sessionid$</SessionID>
    <TimeStamp>$timestamp$</TimeStamp>
    <EchoData/>
    <SystemFields/>
    </Header>
    <Body>
    <EventTicketHold>
    <EventID>$eventid$</EventID>
    <SectionID>$sectionid$</SectionID>
    <Qty>$qty$</Qty>
    <PLU>$plu$</PLU>
    </EventTicketHold>
    </Body>
    </Envelope>
    """
    cmd = cmd.replace("$messageid$",messageid)
    cmd = cmd.replace("$sessionid$",str(sessionid))
    cmd = cmd.replace("$timestamp$",getTimeStamp())
    cmd = cmd.replace("$eventid$",str(eventid))
    cmd = cmd.replace("$sectionid$",str(sectionid))
    cmd = cmd.replace("$qty$",str(qty))
    cmd = cmd.replace("$plu$",item.getPLU())
    response = post2eGalaxy(env,cmd)
    if response:
        event = xml2Dict(response)['Envelope']['Body']['Status']
        if event.get('StatusText') == 'OK':
            return 1,xml2Dict(response)['Envelope']['Body']['EventTicketHoldResponse']['CapacityID']
        return 0,xml2Dict(response)['Envelope']['Body']['Error']['ErrorText']
    return -1,'No reponse'

def confirmOrder_3(orderline,messageid,sessionid,customerid,visitdate):
    stamp = datetime.today().strftime("%Y%m%d%H%M%S")
    govid = 'gov' + stamp
    galid = 'GAL' + stamp
    endorsid = 'endors_' + stamp
    orderdate = orderline.getCreateDate()
    cmd_orderline_payment = """
    <OrderLine>
    	<DetailType>2</DetailType>
    	<Description>63</Description>
    	<Qty>0</Qty>
    	<Amount>{}</Amount>
    	<Total>{}</Total>
    	<PaymentCode>63</PaymentCode>
    	<PaymentDate>{}</PaymentDate>
    	<Endorsement>{}</Endorsement>
    </OrderLine>
    """
    orderline_payment = cmd_orderline_payment.format(
        orderline.getOrderlineAmount(),
        orderline.getOrderlineAmount(),
        orderdate,
        endorsid)
    real_orderlines = orderline.toXMLString() + orderline_payment
    cmd = """
    <Envelope
    	xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    	<Header>
    		<SourceID>GAL</SourceID>
    		<MessageID>$messageid$</MessageID>
    		<MessageType>Orders</MessageType>
    		<TimeStamp>$timestamp$</TimeStamp>
    		<EchoData/>
    		<SystemFields/>
    	</Header>
    	<Body>
    		<Orders>
    			<Order>
    				<OrderID>$galid$</OrderID>
    				<OrderCommand>Add</OrderCommand>
    				<SessionID>$sessionid$</SessionID>
    				<CustomerID>$customerid$</CustomerID>
    				<OrderDate>$orderdatetime$</OrderDate>
    				<OrderTotal>$ordertotal$</OrderTotal>
    				<OrderStatus>2</OrderStatus>
    				<OrderContact>
    					<Contact>
    					<FirstName>kevin</FirstName>
    					<LastName>wu</LastName>
    					<Email>tradeclient@tradeclient.com</Email>
    					<IdentificationNo>$govid$</IdentificationNo>
    					</Contact>
    				</OrderContact>
    				<GroupVisit>
    					<VisitDate>$visitdate$</VisitDate>
    				</GroupVisit>
    				<Shipping>
    					<DeliveryMethod>11</DeliveryMethod>
    					<DeliveryDetails>Galasys</DeliveryDetails>
    				</Shipping>
    				<OrderLines>
                        $ticketsorderlines$
                    </OrderLines>
    				<UserFields>
    					<UserField2>YES</UserField2>
    					<UserField3>PYTHON</UserField3>
    				</UserFields>
    			</Order>
    		</Orders>
    	</Body>
    </Envelope>
    """
    cmd = cmd.replace("$messageid$",messageid)
    cmd = cmd.replace("$timestamp$",getTimeStamp())
    cmd = cmd.replace("$galid$",galid)
    cmd = cmd.replace("$sessionid$",sessionid)
    cmd = cmd.replace("$customerid$",customerid)
    cmd = cmd.replace("$orderdatetime$",orderdate)
    cmd = cmd.replace("$ordertotal$",str(orderline.getOrderlineAmount()))
    cmd = cmd.replace("$govid$",govid)
    cmd = cmd.replace("$visitdate$",visitdate)
    cmd = cmd.replace("$ticketsorderlines$",real_orderlines)
    response = post2eGalaxy(env,cmd)
    if response:
        body = xml2Dict(response)['Envelope']['Body']
        if body.get('CreateTransactionResponse'):
            return body['CreateTransactionResponse']['TransactionData']['OrderID'],endorsid
        return 0,0
    return 0,0
    
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

def queryEventID(messageid,startd,endd,item):
    cmd = """
    <?xml version="1.0" encoding="UTF-8"?>
    <Envelope>
    <Header>
    <SourceID>GAL</SourceID>
    <MessageID>$messageid$</MessageID>
    <MessageType>QueryEvents</MessageType>
    <TimeStamp>$timestamp$</TimeStamp>
    </Header>
    <Body>
      <QueryEvents>
         <EventRangeBeginDate>$startdate$</EventRangeBeginDate>
         <EventRangeEndDate>$enddate$</EventRangeEndDate>
         <EventTypeID>$eventtypeid$</EventTypeID>
         <PLU>$plu$</PLU>
      </QueryEvents>
    </Body>
    </Envelope>
    """
    cmd = cmd.replace("$messageid$",messageid)
    cmd = cmd.replace("$timestamp$",getTimeStamp())
    cmd = cmd.replace("$startdate$",startd + ' 00:00:00')
    cmd = cmd.replace("$enddate$",endd + ' 23:59:00')
    cmd = cmd.replace("$eventtypeid$",str(item.getEventTypeID()))
    cmd = cmd.replace("$plu$",item.getPLU())
    response = post2eGalaxy(env,cmd)
    if response:
        body = xml2Dict(response)['Envelope']['Body']
        if body.get('Events'):
            event = body['Events']['Event']
            return event['EventID'],event['ResourceID']
        return 0,0
    return 0,0


def queryItems(customerid,messageid):
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
    cmd = cmd.replace("$messageid$",messageid)
    cmd = cmd.replace("$timestamp$",getTimeStamp())
    cmd = cmd.replace("$customerid$",customerid)
    response = post2eGalaxy(env,cmd)
    if response:
        body = xml2Dict(response)['Envelope']['Body']
        if int(body['Status']['StatusCode']) == 0:
            itemlist = body['ItemList']
            if itemlist:
                items = []
                for item in itemlist['Item']:
                    t_item = None
                    t_item = Item( item['PLU'] , item['Name'] , item['Description'] , item['Price'] , item['EventTypeID'] , item['EventID'] , item['SectionID'] , item['Kind'] , None)
                    if item.get('PackageDetails'):
                        for package in item['PackageDetails']['PackageDetail']:
                            t_item.addPackageDetails( Item( package['PLU'] , package['Name'] , package['Description'] , package['Price'] , package['EventTypeID'] , package['EventID'] , package['SectionID'] , package['Kind'] , None ) )
                    items.append(t_item)
                return 1,items
            else:
                mylogger.warning("queryItems no items in response")
                return 0,"queryItems no items in response"
        else:
            return 0,body['Errors']['Error']['ErrorText']
    else:
        mylogger.warning("queryItems error in response")
        return 0,"queryItems error in response"

def generateOrderlines(item,qty,eventid,capacityid,createdate):
    pass

def getTimeStamp():
    return datetime.today().strftime("%Y-%m-%d %H:%M:%S")

def getNextDay(dd):
    return (datetime.strptime(dd,"%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    

def post2eGalaxy(enviroment,xmlrequest):
    if enviroment == 'qa':
        url = url_qa
    if enviroment == 'dev':
        url = url_dev
    if enviroment == 'lt':
        url = url_lt
    mylogger.debug("request: " + xmlrequest)
    try:
        ret = post(url=url,data=xmlrequest.encode('utf-8'),headers={'Content-Type':'application/xml','charset':'utf-8'},timeout=60)
        mylogger.debug("response: " + ret.content.decode('utf-8'))
        if ret.status_code == 200:
            return ret.content.decode('utf-8')
        return None
    except postexcept.HTTPError as e:
        mylogger.error("call eGalaxy error: " + str(e))
        return None

def getItemsByKindID(itemlist,**kwargs):
    if kwargs.get('KindIDs'):
        tktlist = []
        for i in itemlist:
            if i.getKindID() in kwargs['KindIDs']:
                tktlist.append(i)
        return tktlist
    else:
        return itemlist
    
def findItem(plu,items):
    for i in items:
        if i.findPLU(plu):
            return i
    return None

def getProducts(custid):
    mylogger.info("Environment: " + env)
    msgid = getNextMessageID()
    customerid = custid
    kindids = (1,2,15)
    flag,items = queryItems(customerid,msgid)
    if flag > 0:
        tktitems = getItemsByKindID(items,KindIDs=kindids)
        return flag,tktitems
    return flag,items
    #for item in tktitems:
    #    print(item.toStringBrief())

def checkItemAvailable(plu,items,visitdate):
    mylogger.info("Environment: " + env)
    msgid = getNextMessageID()
    item = findItem(plu,items)
    if item:
        if item.getKindID() == 1:
            eventid,sectionid = queryEventID(msgid,visitdate,visitdate,item)
            if int(eventid) > 0:
                return 1,item
        if item.getKindID() == 15:
            for subitem in item.getPackageDetails():
                eventid,sectionid = queryEventID(msgid,visitdate,visitdate,subitem)
                if int(eventid) == 0:
                    return 0,visitdate
                visitdate = getNextDay(visitdate)
            return 1,item
        if item.getKindID() == 2:
            return 1,item
    return 0,visitdate

def holdEvents(plu,qty,item,visitdate,messageid):
    mylogger.info("Environment: " + env)
    # authenticate
    msgid = messageid
    username_galaxy = "RZME" #7104
    password_galaxy = "Disney001"

    flag,sessionid = authenticate_1(username_galaxy,password_galaxy,msgid)
    if not flag:
        mylogger.error("auth error: " + sessionid)
        return None
    mylogger.debug('auth sessionid: ' + sessionid)

    orderlines = None
    createdate = getTimeStamp()
    #item = findItem(plu,items)
    startdate = enddate = visitdate

    mylogger.debug("Hold Event For PLU: " + plu)

    if item:
        if item.getKindID() == 15:
            orderlines = OrderLine(item,qty,0,0,createdate)
            for subitem in item.getPackageDetails():
                eventid,sectionid = queryEventID(msgid,startdate,enddate,subitem)
                if int(eventid) > 0:
                    mylogger.debug('eventid: ' + eventid)
                    mylogger.debug('sectionid: ' + sectionid)
                    ok,capacityid = EventTicketHold_2(msgid,sessionid,eventid,qty,subitem,sectionid)
                    if ok > 0:    
                        mylogger.debug('capacityid: ' + capacityid)
                        orderlines.addSubItem(OrderLine(subitem,qty,eventid,capacityid,createdate))
                    else:
                        msg = capacityid
                        mylogger.error("query capacity ID error: " + msg)
                        return 0,msg
                else:
                    mylogger.error("query eventID error")
                    return 0,"query eventID error"
                startdate = enddate = getNextDay(startdate)
            mylogger.debug(orderlines.toXMLString())

        if item.getKindID() == 1:
            eventid,sectionid = queryEventID(msgid,startdate,enddate,item)
            if int(eventid) > 0:
                mylogger.debug('eventid: ' + eventid)
                ok,capacityid = EventTicketHold_2(msgid,sessionid,eventid,qty,item,sectionid)
                if ok > 0:
                    mylogger.debug('capacityid: ' + capacityid)
                    orderlines = OrderLine(item,qty,eventid,capacityid,createdate)
                else:
                    msg = capacityid
                    mylogger.error("query capacity ID error: " + msg)
                    return 0,msg
            else:
                mylogger.error("query eventID error")
                return 0,"query eventID error"
            mylogger.debug(orderlines.toXMLString())
    
        if item.getKindID() == 2:
            orderlines = OrderLine(item,qty,0,0,createdate,1)
            mylogger.debug(orderlines.toXMLString())
        
        return 1,{'orderlines':orderlines,'sessionid':sessionid,'visitdate':visitdate}
    
def confirmOrder(ret_holdevent,customerid,messageid):
    mylogger.info("Environment: " + env)
    orderlines = ret_holdevent['orderlines']
    sessionid = ret_holdevent['sessionid']
    visitdate = ret_holdevent['visitdate']
    if orderlines:
        orderid,endorsid = confirmOrder_3(orderlines,messageid,sessionid,customerid,visitdate)
        if orderid:
            mylogger.debug("GAL order ID: " + str(orderid))
            mylogger.debug("Endorsment ID: " + str(endorsid))
            return 1,"GAL ID=" + str(orderid) + ", EndorsID=" + str(endorsid)
        return 0,"Confirm Order Failed"
    return 0,"No OrderLines in Confirm Order Process"



if __name__ == "__main__":
    InitLogger()
    username_galaxy = "RZME1" #7104
    password_galaxy = "Disney001"
    env = 'qa'
    showENV()
    # query items
    msgid = getNextMessageID()
    customerid = '170'
    kindids = (1,2,15)
    items = queryItems(customerid,msgid)
    tktitems = getItemsByKindID(items,KindIDs=kindids)
    for item in tktitems:
        print(item.toStringBrief())

    # authenticate
    msgid = getNextMessageID()
    sessionid = authenticate_1(username_galaxy,password_galaxy,msgid)
    print('auth sessionid: ' + sessionid)

    # query events
    startdate = enddate = datetime.today().strftime('%Y-%m-%d')
    visitdate = startdate
    qty = 1
    #plu = 'SHTPP2OLCET'
    plu = 'SHTP01OLRET'
    orderlines = None
    createdate = getTimeStamp()

    item = findItem(plu,tktitems)

    if (item.getKindID() == 15) and item:
        orderlines = OrderLine(item,qty,0,0,createdate)
        for subitem in item.getPackageDetails():
            eventid = queryEventID(msgid,startdate,enddate,subitem)
            if int(eventid) > 0:
                mylogger.debug('eventid: ' + eventid)
                ok,capacityid = EventTicketHold_2(msgid,sessionid,eventid,qty,subitem)
                if ok > 0:    
                    mylogger.debug('capacityid: ' + capacityid)
                    orderlines.addSubItem(OrderLine(subitem,qty,eventid,capacityid,createdate))
                else:
                    mylogger.error("query capacity ID error: " + capacityid)
                    break
            else:
                mylogger.error("query eventID error")
                break
            startdate = enddate = getNextDay(startdate)
        mylogger.debug(orderlines.toXMLString())

    if item.getKindID() == 1 and item:
        eventid = queryEventID(msgid,startdate,enddate,item)
        if int(eventid) > 0:
            mylogger.debug('eventid: ' + eventid)
            ok,capacityid = EventTicketHold_2(msgid,sessionid,eventid,qty,item)
            if ok > 0:
                mylogger.debug('capacityid: ' + capacityid)
                orderlines = OrderLine(item,qty,eventid,capacityid,createdate)
            else:
                mylogger.error("query capacity ID error: " + capacityid)
        else:
            mylogger.error("query eventID error")
        mylogger.debug(orderlines.toXMLString())
    
    if item.getKindID() == 2 and item:
        orderlines = OrderLine(item,qty,0,0,createdate,1)
        mylogger.debug(orderlines.toXMLString())

    if orderlines:
        orderid = confirmOrder_3(orderlines,msgid,sessionid,customerid,visitdate)
        mylogger.debug("GAL order ID: " + str(orderid))



 
    