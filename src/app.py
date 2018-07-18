# -*- coding:UTF-8 -*-
import urllib
import urllib.parse
import urllib.request
import re
import os
import time
import json
import threading

#抓取json
def getJSON(period,retries):
    # period = "1d"
    # period = "1w"
    # period = "1m"
    # period = "1y"
    try:
        params = urllib.parse.urlencode({"period":period,"format":"json"})
        f = urllib.request.urlopen("https://yande.re/post/popular_recent?%s" % params)
        print("/////// yande START ///////")
        return f.read()
    except Exception as e:
        if retries > 0:
            print("getJSON Try Again (Left %d time(s))" % retries)
            return getJSON(host,period,retries - 1)
        else:
            print("getJSON Failed")
            return

#根据 url 数组，下载图片
def saveImg(imglist):
    imglist = json.loads(imglist)
    filename = "image"
    now = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    print("===== %s =====" % now)
    Headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '  
                             '(KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',  
               "Referer":""}
    x = 0

    log = open("idlog.txt","r+")
    logstr = log.read()
    idlog = logstr.split(",")
    print(logstr)
    
    theretries = 5;

    def downloadurl(imgjson, retries):
        nonlocal x
        nonlocal idlog
        theid = str(imgjson["id"])
        url = imgjson["file_url"]
        Headers['Referer'] = "https://yande.re/post/show/" + theid
        # print(url)
        try:
            req = urllib.request.Request(url, None, Headers)
            res = urllib.request.urlopen(req)
        # except urllib.error.HTTPError:  
        #     url = url.replace('.jpg', '.png')  
        #     req = urllib.request.Request("http:"+url, None, Headers)
        #     res = urllib.request.urlopen(req)
            path = filename+"/"+theid+".jpg"
            isexist = os.path.exists(path)
            if (isexist == False) and (theid not in idlog):

                idlog.append(theid)
                # idlogstr = ','.join(idlog)
                log.write(",%s" % theid)
                f = open(path,"wb")
                f.write(res.read())
                print("saved %s picture" % (x+1))
                res.close()
                f.close()
                x += 1
            else:
                print("had the picture")
                if (theid not in idlog):
                    idlog.append(theid)
                    log.write(",%s" % theid)
                    
        except urllib.error.HTTPError:
            # print(e.message)
            if retries > 0:
                print("downloadurl Try Again (Left %d time(s))" % retries)
                return downloadurl(imgjson, retries - 1)
            else:
                print("get Failed")
                return

    threads = []
    for imgjson in imglist:
        t = threading.Thread(target = downloadurl,args = (imgjson, theretries))
        threads.append(t)
    for th in threads:
        th.setDaemon(True)
        #time.sleep(1)
        th.start()
        while True:
            if (len(threading.enumerate()) < 3):
                break;       
    for th in threads:
        th.join()
    idlogstr = ','.join(idlog)
    # print("idlogstr:%s" % idlogstr)
    # log.write(idlogstr)
    log.close()
    print("=====================\r\n saved %d picture(s)." % x)

print("======== daily ========")
imglist = getJSON("1d",5)
saveImg(imglist)
print("======== weekly ========")
imglist = getJSON("1w",5)
saveImg(imglist)
print("======== monthly ========")
imglist = getJSON("1m",5)
saveImg(imglist)
print("======== yearly ========")
imglist = getJSON("1y",5)
saveImg(imglist)
print("======== END ========")
input()