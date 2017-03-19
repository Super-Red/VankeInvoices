import requests
import os
import re
import csv

session = requests.Session()
Cookies_dict = {
    "SESSION": "ba135020-12c2-44bd-a237-76d66fde85e7",
    "SERVERID": "8fdc1880ed828cb90add34757d29f397|1487308322|1487308186"
    }
cookies = requests.utils.cookiejar_from_dict(Cookies_dict, cookiejar=None, overwrite=True)
session.cookies = cookies
with open("/Users/red/Desktop/ss.csv", 'r') as csvFile:
    urls = []
    reader = csv.reader(csvFile)
    count = 1
    totalAmount = 0
    for i in reader:
        if ((i[2] in ("1", "5")) and (float(i[5]) >= 0)):
            userData = {
                "service": "IBIN90",
                "method": "queryImagePath",
                "eiinfo": '{attr:{"invoiceId":"%s"},blocks:{}}' % i[1]
                }
            # get pic_urls
            r = session.post("https://www.xforceplus.com/imsc/EiService", data=userData)
            url = re.findall(r'"imagePath":(.+?)",', r.text)[0]
            invoices_pic_url = "https://www.xforceplus.com/imsc" + url[2:]
            urls.append(invoices_pic_url)

            pic = session.get(invoices_pic_url, stream=True)
            filename = "%d.jpg" % (count)
            if pic.status_code == 200:
                with open(os.path.join("/Users/red/Desktop/ss", filename), "wb") as f:
                    for chunk in pic:
                        f.write(chunk)
            else: 
                print("%s.jpg failed" % (i[0]))
            print("%s.jpg done" % (i[0]))
            count += 1
            totalAmount += float(i[5])
print("All Done!")
print("The total amount of invoices done is {}".format(totalAmount))
