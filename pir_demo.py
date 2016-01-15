#!/usr/bin/python
import MySQLdb
import _mysql
# import psycopg2
import xml.dom.minidom 
import sys
import re
import cgi
import cgitb
import Common
import rotational
import relational
# import tabbed
cgitb.enable()

userId = 2424
local = 0
cursor = 0
pirDoc = xml.dom.minidom.Document()
if (local):
   # cursor = MySQLdb.connect(user="root",db="jripples_usem").cursor() 
   cursor = MySQLdb.connect(host=".awardspace.net",user="1764220_pir",passwd="", \
                               db="1764220_pir").cursor() 
   f = open("tests.xml")
   pirDoc = xml.dom.minidom.parseString(f.read())
else:
   # conn = psycopg2.connect("dbname='1764220_george' user='1764220_george' \
   #       host='pgdb1.runhosting.com' password=''")
   # cursor = conn.cursor()
   cursor = MySQLdb.connect(host="pdb19.awardspace.net",user="1764220_pir",passwd="", \
                               db="1764220_pir").cursor() 
   xml_str = sys.stdin.read()
   xml_str = re.sub('>\s*<','><',xml_str)
   pirDoc = xml.dom.minidom.parseString(xml_str)

pirEle = pirDoc.getElementsByTagName("pirElement")[0]
screenName = pirEle.getElementsByTagName("screenName")[0]. \
                  childNodes[0].nodeValue
if (screenName == "rotational"):
   rotational.rotational(pirEle,cursor)
if (screenName == "tabbed"):
   tabbed.tabbed(userId,pirEle,cursor)
if (screenName == "relational"):
   relational.relational(userId,pirEle,cursor)
print "Content-type: text/xml\n";
print "<rsDocument>"
print pirEle.toprettyxml()
print "</rsDocument>"
f = open('show_xml.xml', 'w')
f.write(pirDoc.toprettyxml())
f.close
