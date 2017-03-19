#-*-encoding:utf-8-*-

'''
Author:     Super_Red
Date:       12/12/2016
Describe:   Download invoices from the web
'''

import requests
import csv
import os
import json
import re
import csv 

class InvoiceWeb(object):

    def __init__(self, session, serverID, search_nd, search_eiinfo, pages, file):
        self.file = file
        os.mkdir("/Users/red/Desktop/{file}".format(file=self.file))
        self.session = requests.Session()
        self.cookies_dict = {   "SESSION" : session,
                                "SERVERID" : serverID}
        self.session.cookies = requests.utils.cookiejar_from_dict(self.cookies_dict, cookiejar=None, overwrite=True)
        self.pages_number = pages
        self.pages = []
        self.findPages(search_nd, search_eiinfo)

    def findPages(self, search_nd, search_eiinfo):
        userData = {    "_search" : "false",
                        "nd" : search_nd,
                        "rows" : "100",
                        "page" : "",
                        "sord" : "asc",
                        "eiinfo" : search_eiinfo}
        for i in range(1, self.pages_number+1):
            userData["page"] = i
            html = self.session.post("https://www.xforceplus.com/imsc/DispatchAction.do?efFormEname=IBIN96&serviceName=IBIN90&methodName=queryInvoiceJSON", data=userData)
            self.pages.append(html.text)
            print ("page%d has stored!" % i )
        print ("All pages are stored")

    def saveToFile(self):
        with open("/Users/red/Desktop/{file}/invoiceDetail.csv".format(file=self.file), 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(("num", "invoicesID", "status", "date", "invoiceNo", "amountWithoutTax", "taxAmount", "amountWithTax"))
            for index, page_html_text in enumerate(self.pages):
                status = re.findall(r'"cloudScheck":"(.+?)"', page_html_text)
                invoicesId = re.findall(r'"invoiceId":"(.+?)"', page_html_text)
                createTime = re.findall(r'"createTime":"(.+?)"', page_html_text)
                invoiceNo = re.findall(r'"invoiceNo":"(.+?)"', page_html_text)
                amountWithTax = re.findall(r'"amountWithTax":(.+?),', page_html_text)
                amountWithoutTax = re.findall(r'"amountWithoutTax":(.+?),', page_html_text)
                taxAmount = re.findall(r'"taxAmount":(.+?),', page_html_text)
                for j in range(len(status)):
                    if (status[j] in ("1", "5")):
                        writer.writerow((j, invoicesId[j], status[j], createTime[j][:8], invoiceNo[j], amountWithoutTax[j], taxAmount[j], amountWithTax[j]))
                        print ("No.{} in page{} has SAVED!".format(j, index+1))

    def sortFile(self):
        with open("/Users/red/Desktop/{file}/invoiceDetail.csv".format(file=self.file), 'r') as csvFile:
            all_data = list(csv.reader(csvFile))
        all_data_sorted = sorted(all_data[1:], key = lambda x : float(x[7]), reverse = True)
        with open("/Users/red/Desktop/{file}/invoiceDetail_sorted.csv".format(file=self.file), 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow((all_data[0]))
            for index, value in enumerate(all_data_sorted):
                writer.writerow(([index+1, ] + value[1:]))
        print ("File sorted!")

    def downloadInvoice(self, file, mininum=0):
        os.mkdir("/Users/red/Desktop/{file}/invocies".format(file=self.file))
        with open("/Users/red/Desktop/{file}/invoiceDetail_sorted.csv".format(file=self.file), 'r') as csvFile:
            urls = []
            reader = csv.reader(csvFile)
            count = 1
            totalAmount = 0
            for value in reader:
                if ((value[2] in ("1", "5")) and (float(value[7]) >= mininum)):
                    userData = {
                        "service": "IBIN90",
                        "method": "queryImagePath",
                        "eiinfo": '{attr:{"invoiceId":"%s"},blocks:{}}' % value[1]
                        }
                    # get pic_urls
                    r = self.session.post("https://www.xforceplus.com/imsc/EiService", data=userData)
                    url = re.findall(r'"imagePath":(.+?)",', r.text)[0]
                    invoices_pic_url = "https://www.xforceplus.com/imsc" + url[2:]
                    urls.append(invoices_pic_url)

                    pic = self.session.get(invoices_pic_url, stream=True)
                    filename = "%d.jpg" % (count)
                    if pic.status_code == 200:
                        with open("/Users/red/Desktop/{file}/invocies/{filename}".format(file=self.file, filename=filename), "wb") as f:
                            for chunk in pic:
                                f.write(chunk)
                    else: 
                        print("%s.jpg failed" % (value[0]))
                    print("%s.jpg downloaded" % (value[0]))
                    count += 1
                    totalAmount += float(value[5])
        print("All Downloaded!")
        print("The total amount of invoices done is {}".format(totalAmount))

    def run(self):
        self.saveToFile()
        self.sortFile()
        self.downloadInvoice()

##############################################################################################################################################################################
#
#      INPUT ZONE  
#
##############################################################################################################################################################################

# login_url = "https://vat.servingcloud.com/"

session = "5a5a8434-ebf7-4f14-8886-cc3ea9e62e53"
serverID = "2ef99f60200a84f832b7659c657a0bfe|1487314088|1487314060"
search_nd = "1487314209668"
search_eiinfo = '{attr:{"settlementStatus":"","scanBatchNo":"","invoiceNo":"","invoiceCode":"","paperDrewDateScope":"01/01/2015 - 02/17/2017","invoiceType":"","sellerTaxNo":"","settlementNo":"","purchaserCode":"91350581081636026X01","purchaserManageUnit":"","sellerName":"","taxNo":"","taxName":"","amountWithTaxBegin":"","amountWithTaxEnd":"","authTimeScope":"","authResult":"","scanTimeScope":"","drawoutTimeScope":"","invoiceOrig":"","expressStatus":"","payStatus":"","auditStatus":"","isNeedAudit":"","cloudStatus":"","cooperateFlag":"","imageStatus":"","scanMethod":"","status1":"false","status4":"false","status2":"false","status3":"false","redTime":"false","redLetter":"false","twoCodeFlag":"false","authResultAndELFlag":"false","electronicInvoiceFlag":"","invoiceItemMode":"","electronicLedgerFlag":"","electronicLedgerReceiveFlag":"","ensureTimeScope":"","electronicLedgerTimeScope":"","tp":"","tpBatchNo":"","isNeedAuth":"","electronicInFlag":"null","cloudIdentifyRemark":""},blocks:{}}'
pages = 4
file = "ss"
mininum = 0

##############################################################################################################################################################################
#
#      INPUT ZONE
#
##############################################################################################################################################################################

test = InvoiceWeb(session, serverID, search_nd, search_eiinfo, pages, file)
test.run()
