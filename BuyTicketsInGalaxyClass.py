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
    
    def toStringBrief(self):
        return "{},{},{},{}".format(self.plu,self.name,self.price,self.eventtypeid)
    
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
    def __init__(self,detailid,plu,desc,qty,amount,eventid,capacityid,createdate):
        self.detailid = detailid
        self.plu = plu
        self.desc = desc
        self.qty = qty
        self.amount = amount
        self.eventid = eventid
        self.capacityid = capacityid
        self.createdate = createdate

    def toXMLString(self)->str:
        orderline = """
                    <OrderLine>
						<DetailType>{}</DetailType>
						<PLU>{}</PLU>
						<Description>{}</Description>
						<Qty>{}</Qty>
						<Amount>{}</Amount>
						<Total>{}</Total>
						<EventID>{}</EventID>
						<SectionID>1</SectionID>
						<ResourceID>1</ResourceID>
						<CapacityID>{}</CapacityID>
						<Package/>
						<Seats/>
						<CreateDate>{}</CreateDate>
					</OrderLine>
                    """
        return orderline.format(self.detailid,self.plu,self.desc,self.qty,self.amount,self.qty*self.amount,self.eventid,self.capacityid,self.createdate)
