#!/usr/bin/env python
# coding: utf-8
from datetime import datetime


class Item(object):
    def __init__(self,plu,name,desc,price,eventtypeid,eventid,sectionid,kindid,packagedetails):
        self.plu = plu
        self.name = name
        self.desc = desc
        self.price = price
        self.eventtypeid = eventtypeid
        self.eventid = eventid
        self.sectionid = sectionid
        self.kindid = kindid
        if not packagedetails:
            self.packagedetails = []

    def isPackage(self):
        if self.packagedetails:
            return 1
        return 0
    
    def getPackageDetails(self):
        return [ i for i in self.packagedetails]

    def getSectionID(self):
        if self.sectionid == None:
            return 0
        return int(self.sectionid)

    def getPrice(self):
        return self.price

    def getPLU(self):
        return self.plu
    
    def getDesc(self):
        return self.desc
    
    def getEventTypeID(self):
        if self.eventtypeid == None:
            return 0
        return int(self.eventtypeid)

    def getKindID(self):
        if self.kindid == None:
            return 0
        return int(self.kindid)
    
    def findPLU(self,plu):
        if self.plu == plu:
            return self
        return None

    
    def toStringBrief(self):
        return "{},{},{}".format(self.plu,self.name,self.price)
    
    def toStringBriefPackage(self):
        if self.isPackage():
            ret = ''
            for pkg in self.packagedetails:
                ret = ret + pkg.toStringBrief()
                ret = ret + " / "
            return ret
        return "no package details"

    def addPackageDetails(self,pkg):
        self.packagedetails.append(pkg)

class OrderLine(object):
    def __init__(self,item,qty,eventid,capacityid,createdate,passstatus=0):
        # detailtypeid # 1 ticket, 2 payment, 10 package
        self.item = item
        self.qty = qty
        self.eventid = eventid
        self.capacityid = capacityid
        self.createdate = createdate
        self.suborderlines = []
        self.passstatus = passstatus
    
    def addSubItem(self,suborderline):
        self.suborderlines.append(suborderline)
        return self

    def find_w_EventID(self,eventid):
        if int(self.eventid) == int(eventid):
            return self
        return None

    def getItem(self):
        return self.item

    def getQty(self):
        return int(self.qty)

    def getEventID(self):
        return self.eventid

    def getCapacityID(self):
        return self.capacityid

    def setCapacityID(self,eventid):
        self.eventid = eventid
    
    def getCreateDate(self):
        return self.createdate

    def setSubOrderLineCapacityID(self,eventid):
        for subitem in self.suborderlines:
            if subitem.find_w_EventID(eventid):
                subitem.setCapacityID(eventid)
            return 1
        return 0

    def toXMLString(self):
        return self.__str__()

    def __str__(self):
        if self.passstatus:
            orderline = """
            <OrderLine>
				<DetailType>8</DetailType>
				<PLU>{}</PLU>
				<Description>{}</Description>
				<Qty>{}</Qty>
				<Amount>{}</Amount>
				<Total>{}</Total>
				<EventID/>
				<SectionID/>
				<Package/>
				<Seats/>
				<CreateDate>{}</CreateDate>
				<Pass>
					<FirstName>pass_fn</FirstName>
					<LastName>pass_ln</LastName>
				</Pass>
			</OrderLine>
            """
            return orderline.format(
                self.item.getPLU(),
                self.item.getDesc(),
                self.qty,
                self.qty * self.item.getPrice(),
                self.qty * self.item.getPrice(),
                self.createdate
            )
        if self.suborderlines:
            result_subitems = ''
            for suborderline in self.suborderlines:
                orderline_subitem = """
                <PackageDetail>
			    <PLU>{}</PLU>
			    <Price>0</Price>
			    <Amount>{}</Amount>
			    <Total>{}</Total>
			    <EventID>{}</EventID>
			    <ResourceID>1</ResourceID>
			    <CapacityID>{}</CapacityID>
			    <Qty>{}</Qty>
			    <CreateDate>{}</CreateDate>
                </PackageDetail>
                """
                subitem = suborderline.getItem()

                result_subitems = result_subitems + orderline_subitem.format(
                    subitem.getPLU(),
                    subitem.getPrice()*suborderline.getQty(),
                    subitem.getPrice()*suborderline.getQty(),
                    suborderline.getEventID(),
                    suborderline.getCapacityID(),
                    suborderline.getQty(),
                    suborderline.getCreateDate()
                    )
            orderline_pkgheader = """
            <OrderLine>
			<DetailType>10</DetailType>
			<PLU>{}</PLU>
			<Description>{}</Description>
			<Qty>{}</Qty>
			<Amount>{}</Amount>
			<Total>{}</Total>
			<EventID/>
			<SectionID/>
			<Package>{}</Package>
			<Seats/>
			</OrderLine>
            """
            result = orderline_pkgheader.format(
                self.item.getPLU(),
                self.item.getDesc(),
                self.qty,
                self.qty*self.item.getPrice(),
                self.qty*self.item.getPrice(),result_subitems
                )
            return result
        
        orderline = """
        <OrderLine>
        <DetailType>1</DetailType>
        <PLU>{}</PLU>
        <Description>{}</Description>
        <Qty>{}</Qty>
        <Amount>{}</Amount>
        <Total>{}</Total>
        <EventID>{}</EventID>
        <SectionID>{}</SectionID>
        <ResourceID>1</ResourceID>
        <CapacityID>{}</CapacityID>
        <Package/>
        <Seats/>
        <CreateDate>{}</CreateDate>
        </OrderLine>
        """
        return orderline.format(
            self.item.getPLU(),
            self.item.getDesc(),
            self.qty,
            self.item.getPrice(),
            self.qty*self.item.getPrice(),
            self.eventid,
            self.item.getSectionID(),
            self.capacityid,
            self.createdate
            )

    def getOrderlineAmount(self):
        return self.qty*self.item.getPrice()