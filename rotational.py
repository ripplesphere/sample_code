import xml.dom.minidom
import MySQLdb
#import psycopg2
import _mysql
import urllib
import Common

pirDoc = xml.dom.minidom.Document()
idForNext = 0

def rotational(pirEle, cursor):
   if (pirEle.getElementsByTagName("action")):
      action(pirEle,cursor)
   if (pirEle.getElementsByTagName("selection")):
      selection(pirEle,cursor)
def action(pirEle,cursor):
   actionEle = pirEle.getElementsByTagName("action")[0]
   objectType = Common.checkXMLValue("object_type",actionEle)
   actionType = Common.checkXMLValue("action_type",actionEle)
   if (actionType == "delete"):
      objectId = Common.checkXMLValue("object_id",actionEle)
      cursor.execute("""delete from rs_%s where id = %s""" % \
            (objectType,objectId))
      cursor.execute("""delete from rs_person_story_photo_rel where %s_id = %s""" \
                        % (objectType,objectId))
      cursor.execute("""update rs_person set father_id = 0 where father_id = %s""" % (objectId))
      cursor.execute("""update rs_person set mother_id = 0 where mother_id = %s""" % (objectId))
      spouseInfo = Common.getSpouseInfo(cursor,objectId)
      if (spouseInfo):
         cursor.execute("""delete from rs_marriage where id = %s""" % (spouseInfo))
   elif (actionType == "connect_objects"):
      connectObjects(actionEle,cursor)
   elif (objectType == "person"):
      personObject(actionEle,cursor,actionType)
   elif (objectType == "story"):
      storyObject(pirEle,cursor,actionType)
   elif (objectType == "photo"):
      photoObject(pirEle,cursor,actionType)
   elif (objectType == "relative"):
      relativeAction(actionEle,cursor,actionType)
def connectObjects(actionEle,cursor):
   objectType = Common.checkXMLValue("object_type",actionEle)
   objectId = Common.checkXMLValue("object_id",actionEle)
   screenType = Common.checkXMLValue("screen_type",actionEle)
   screenId = Common.checkXMLValue("screen_id",actionEle)
   connectionAction = Common.checkXMLValue("connection_action",actionEle)
   if (connectionAction == "connect"):
      cursor.execute("""insert into rs_person_story_photo_rel (%s_id,%s_id) values
                        (%s,%s)""" % (objectType,screenType,objectId,screenId))
   elif (connectionAction == "disconnect"):
      cursor.execute("""delete from rs_person_story_photo_rel where %s_id = %s and
                        %s_id = %s""" \
                        % (objectType,objectId,screenType,screenId))
def relativeAction(actionEle,cursor,actionType):
   if (Common.checkXMLValue("perform",actionEle) == "add"):
      personObject(actionEle,cursor,"add")
      relativeId = Common.checkXMLValue("object_id",actionEle)
      personId = Common.checkXMLValue("person_id",actionEle)
      gender = Common.checkXMLValue("gender",actionEle)
      if (actionType == "addParent"):
         if (gender == "f"):
            sql = """update rs_person set mother_id = %s where id = %s""" % (relativeId,personId)
         else:
            sql = """update rs_person set father_id = %s where id = %s""" % (relativeId,personId)
      else:
         if (gender == "f"):
            sql = """update rs_person set mother_id = %s where id = %s""" % (personId,relativeId)
         else:
            sql = """update rs_person set father_id = %s where id = %s""" % (personId,relativeId)
      cursor.execute(sql)
   elif (Common.checkXMLValue("perform",actionEle) == "connect"):
      childId = Common.checkXMLValue("child_id",actionEle)
      gender = Common.checkXMLValue("gender",actionEle)
      parentId = Common.checkXMLValue("parent_id",actionEle)
      if (gender == "f"):
         sql = """update rs_person set mother_id = %s where id = %s""" % (parentId,childId)
      else:
         sql = """update rs_person set father_id = %s where id = %s""" % (parentId,childId)
   elif (Common.checkXMLValue("perform",actionEle) == "remove"):
      tupleId = Common.checkXMLValue("tuple_id",actionEle)
      attName = Common.checkXMLValue("att_name",actionEle)
      sql = """update rs_person set %s = 0 where id = %s""" % (attName,tupleId)
   cursor.execute(sql)
def personObject(actionEle,cursor,actionType):
   fname = Common.checkXMLValue("fname",actionEle)
   mname = Common.checkXMLValue("mname",actionEle)
   lname = Common.checkXMLValue("lname",actionEle)
   b_date = Common.checkXMLValue("b_date",actionEle)
   if (b_date):
      month,day,year = b_date.split('/')
      b_date = "%s-%s-%s" % (year,month.rjust(2,'0'),day.rjust(2,'0'))
   gender = Common.checkXMLValue("gender",actionEle)
   address,city,state,country,zipcode = getLocation(actionEle)
   if (actionType == "add"):
      cursor.execute("""insert into rs_person (fname, mname, lname,
            b_date, gender, address, city, state, country, zipcode, enterer_id) values
            ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s",1)""" \
            % (fname,mname,lname,b_date,gender,address,city,state,country,zipcode))
      object_id = cursor.lastrowid
      Common.addXMLValue(actionEle,"object_id",str(object_id))
      if (Common.checkXMLValue("connect",actionEle)):
         connectObjects(actionEle,cursor)
      else:
         for objects in actionEle.getElementsByTagName("objects"):
            Common.addXMLValue(objects,"object_id",str(object_id))
   elif (actionType == "update"):
      personId = Common.checkXMLValue("object_id",actionEle)
      cursor.execute("""update rs_person set fname = "%s", mname = "%s", lname = "%s",
            b_date = "%s", gender = "%s", address = "%s", city = "%s", state = "%s", country = "%s",
            zipcode = "%s" where id = %s""" % (fname,mname,lname,b_date,gender,address,city, \
            state,country,zipcode,personId))
      spouseId = Common.checkXMLValue("spouse_id",actionEle)
      spouseInfo = Common.getSpouseInfo(cursor,personId)
      if (spouseInfo):
         if (not spouseId):
            cursor.execute("""delete from rs_marriage where id = %s""" % (spouseInfo[0]))
         elif (spouseId != spouseInfo[0]):
            spouseDate = Common.checkXMLValue("spouse_date",actionEle)
            cursor.execute("""update rs_marriage set partner_a_id = %s, partner_b_id = %s, marriage = %s 
                               where id = %s""" % (personId,spouseId,spouseInfo[0],spouseDate))
      elif (int(spouseId)):
         spouseDate = Common.checkXMLValue("spouse_date",actionEle)
         cursor.execute("""insert into rs_marriage (partner_a_id,partner_b_id,marriage,marriage) values
                        (%s, %s)""" % (personId,spouseId,spouseDate))
def photoObject(pirEle,cursor,actionType):
   actionEle = pirEle.getElementsByTagName("action")[0]
   displayName = Common.checkXMLValue("display_name",actionEle)
   comments = Common.checkXMLValue("comments",actionEle)
   dateTaken = Common.checkXMLValue("date_taken",actionEle)
   if (dateTaken):
      month,day,year = dateTaken.split('/')
      dateTaken = "%s-%s-%s" % (year,month.rjust(2,'0'),day.rjust(2,'0'))
   address,city,state,country,zipcode = getLocation(actionEle)
   objectId = Common.checkXMLValue("object_id",actionEle)
   cursor.execute("""update rs_photo set display_name = "%s", date_taken = "%s", 
         comments = "%s", address = "%s", city = "%s", state = "%s", country = "%s",
         zipcode = "%s" where id = %s""" \
         % (displayName,dateTaken,comments,address,city,state,country,zipcode,objectId))
def storyObject(pirEle,cursor,actionType):
   actionEle = pirEle.getElementsByTagName("action")[0]
   story_text = _mysql.escape_string(urllib.unquote(Common.checkXMLValue("story_text",actionEle)))
   title = _mysql.escape_string(urllib.unquote(Common.checkXMLValue("title",actionEle)))
   startsOn = Common.checkXMLValue("starts_on",actionEle)
   if (startsOn):
      month,day,year = startsOn.split('/')
      startsOn = "%s-%s-%s" % (year,month.rjust(2,'0'),day.rjust(2,'0'))
   endsOn = Common.checkXMLValue("ends_on",actionEle)
   if (endsOn):
      month,day,year = endsOn.split('/')
      endsOn = "%s-%s-%s" % (year,month.rjust(2,'0'),day.rjust(2,'0'))
   address,city,state,country,zipcode = getLocation(actionEle)
   if (actionType == "add"):
      cursor.execute("""insert into rs_story (story_text, title, starts_on, ends_on,
            address, city, state, country, zipcode, enterer_id) values 
            ("%s","%s","%s","%s","%s","%s","%s","%s","%s",1)""" \
            % (story_text,title,startsOn,endsOn,address,city,state,country,zipcode))
      object_id = cursor.lastrowid
      Common.addXMLValue(actionEle,"object_id",str(object_id))
      for objects in pirEle.getElementsByTagName("objects"):
         Common.addXMLValue(objects,"object_id",str(object_id))
      if (Common.checkXMLValue("connect",actionEle)):
         connectObjects(actionEle,cursor)
   elif (actionType == "update"):
      storyId = Common.checkXMLValue("object_id",actionEle)
      cursor.execute("""update rs_story set story_text = "%s", title = "%s", starts_on = "%s",  
            ends_on = "%s", address = "%s", city = "%s", state = "%s", country = "%s",
            zipcode = "%s" where id = %s""" % (story_text,title,startsOn,endsOn,address,city,state, \
            country,zipcode,storyId))
def getLocation(pirEle):
   address_l1 = _mysql.escape_string(urllib.unquote(Common.checkXMLValue("address_l1",pirEle)))
   city = Common.checkXMLValue("city",pirEle)
   state = Common.checkXMLValue("state",pirEle)
   country = Common.checkXMLValue("country",pirEle)
   zipcode = Common.checkXMLValue("zipcode",pirEle)
   return address_l1,city,state,country,zipcode
def selection(pirEle,cursor):
   for objects in pirEle.getElementsByTagName("objects"):
      if (objects.attributes["type"].value == "person"):
         if (Common.checkXMLValue("quanity",objects) == "many"):
            if (Common.checkXMLValue("size",objects) == "all"):
               objectChild = pirDoc.createElement("persons")
               cursor.execute("""select id from rs_person p order by b_date desc""")
               fetchall = cursor.fetchall();
               for row in fetchall:
                  personEle(objectChild,row[0],cursor)
               pirEle.appendChild(objectChild)
            if (Common.checkXMLValue("size",objects) == "all_related"):
               all_related("person","persons","b_date",objects,cursor)
            if (Common.checkXMLValue("size",objects) == "all_minus_related"):
               all_minus_related("person","persons","b_date",objects,cursor)
         if (Common.checkXMLValue("quanity",objects) == "one"):
            objectId = Common.checkXMLValue("object_id",pirEle)
            personEle(pirEle,objectId,cursor)
      if (objects.attributes["type"].value == "story"):
         if (Common.checkXMLValue("quanity",objects) == "many"):
            if (Common.checkXMLValue("size",objects) == "all"):
               objectChild = pirDoc.createElement("stories")
               cursor.execute("""select id from rs_story p order by starts_on desc""")
               fetchall = cursor.fetchall();
               for row in fetchall:
                  storyEle(objectChild,row[0],cursor)
               pirEle.appendChild(objectChild)
            if (Common.checkXMLValue("size",objects) == "all_related"):
               all_related("story","stories","starts_on",objects,cursor)
            if (Common.checkXMLValue("size",objects) == "all_minus_related"):
               all_minus_related("story","stories","starts_on",objects,cursor)
         if (Common.checkXMLValue("quanity",objects) == "one"):
            objectId = Common.checkXMLValue("object_id",pirEle)
            storyEle(pirEle,objectId,cursor)
      if (objects.attributes["type"].value == "photo"):
         if (Common.checkXMLValue("quanity",objects) == "many"):
            if (Common.checkXMLValue("size",objects) == "all"):
               objectChild = pirDoc.createElement("photos")
               cursor.execute("""select id from rs_photo p order by date_taken desc""")
               fetchall = cursor.fetchall();
               for row in fetchall:
                  photoEle(objectChild,row[0],cursor)
               pirEle.appendChild(objectChild)
            if (Common.checkXMLValue("size",objects) == "all_related"):
               all_related("photo","photos","date_taken",objects,cursor)
            if (Common.checkXMLValue("size",objects) == "all_minus_related"):
               all_minus_related("photo","photos","date_taken",objects,cursor)
         if (Common.checkXMLValue("quanity",objects) == "one"):
            objectId = Common.checkXMLValue("object_id",pirEle)
            photoEle(pirEle,objectId,cursor)
      if (objects.attributes["type"].value == "relatives"):
         objectChild = pirDoc.createElement("relatives")
         pirEle.appendChild(objectChild)
         firstOrder = [0]
         if (globals()["idForNext"]):
            firstOrder[0] = globals()["idForNext"]
            personId = globals()["idForNext"]
         else:
            firstOrder[0] = int(Common.checkXMLValue("object_id",objects))
            personId = Common.checkXMLValue("object_id",objects)
         cursor.execute("select mother_id, father_id from rs_person where id = %s" \
                         % (personId))
         parents = cursor.fetchone()
         if (parents):
            motherId,fatherId = parents
            # find children
            cursor.execute("""select id,gender from rs_person 
                     where mother_id = %s or father_id = %s order by b_date desc""" \
                           % (personId,personId))
            fetchall = cursor.fetchall();
            for row in fetchall:
               pE = personEle(objectChild,row[0],cursor)
               firstOrder.append(row[0])
               if (row[1] == "f"):
                  Common.addXMLValue(pE,"relation","daughter")
               else:
                  Common.addXMLValue(pE,"relation","son")
            if (motherId or fatherId): 
               # mother information
               if (motherId): 
                  firstOrder.append(motherId)
                  pE = personEle(objectChild,motherId,cursor)
                  Common.addXMLValue(pE,"relation","mother")
               # father information
               if (fatherId):
                  firstOrder.append(fatherId)
                  pE = personEle(objectChild,fatherId,cursor)
                  Common.addXMLValue(pE,"relation","father")
               # find siblings
               cursor.execute("""select id,gender from rs_person
                  where id != %s and mother_id = %s and father_id = %s 
                  and mother_id != 0 and father_id != 0 order by b_date desc""" \
                  % (int(personId),int(motherId),int(fatherId)))
               fetchall = cursor.fetchall();
               for row in fetchall:
                  if (personId != row[0]):
                     siblingId = row[0]
                     pE = personEle(objectChild,siblingId,cursor)
                     firstOrder.append(siblingId)
                     if (row[1] == "f"):
                        Common.addXMLValue(pE,"relation","sister")
                     else:
                        Common.addXMLValue(pE,"relation","brother")
               # find half-siblings
               cursor.execute("""select id,gender from rs_person 
                        where id != %s and ((mother_id = %s and father_id != %s
                        and mother_id != 0) or (mother_id != %s and father_id = %s 
                        and father_id != 0) or (mother_id = %s and father_id = %s 
                        and mother_id != 0 and father_id = 0) or (mother_id = %s 
                        and father_id = %s and mother_id = 0 and father_id != 0))
                        order by b_date desc""" % (personId,motherId,fatherId, \
                           motherId,fatherId,motherId,fatherId,motherId,fatherId))
               fetchall = cursor.fetchall();
               for row in fetchall:
                  pE = personEle(objectChild,row[0],cursor)
                  firstOrder.append(row[0])
                  if (row[1] == "f"):
                     Common.addXMLValue(pE,"relation","half-sister")
                  else:
                     Common.addXMLValue(pE,"relation","half-brother")
         if (Common.checkXMLValue("relatives_set",objects) == "relatives"):
            backRelation = Common.checkXMLValue("backRelation",objects)
            if (backRelation == "true"):
               globals()["idForNext"] = firstOrder[1]
            objects.appendChild(objectChild)
         elif (Common.checkXMLValue("relatives_set",objects) == "not_relatives"):
            ncChild = pirDoc.createElement("not_relatives")
            # List of persons who can be added as a relative
            cursor.execute("""select id from rs_person order by b_date desc""")
            fetchall = cursor.fetchall();
            for row in fetchall:
               if( not row[0] in firstOrder):
                  personEle(ncChild,row[0],cursor)
            objects.appendChild(ncChild)
def all_related(setType,setName,orderBy,objects,cursor):
   objectType = Common.checkXMLValue("object_type",objects)
   if (globals()["idForNext"]):
      objectId = globals()["idForNext"]
   else:
      objectId = Common.checkXMLValue("object_id",objects)
   objectChild = pirDoc.createElement(setName)
   cursor.execute("""select %s_id from rs_person_story_photo_rel psp, rs_%s ot 
                     where %s_id = %s and %s_id <> 0 and 
                     ot.id = psp.%s_id order by %s desc""" % (setType,setType, \
                           objectType,objectId,setType,setType,orderBy))
   fetchall = cursor.fetchall();
   rowCount = cursor.rowcount
   backRelation = Common.checkXMLValue("backRelation",objects)
   for row in fetchall:
      if (backRelation == "true"):
         globals()["idForNext"] = row[0]
         backRelation = "false"
      globals()[setType+"Ele"](objectChild,row[0],cursor)
   objects.appendChild(objectChild)
def all_minus_related(setType,setName,orderBy,objects,cursor):
   objectType = Common.checkXMLValue("object_type",objects)
   objectId = Common.checkXMLValue("object_id",objects)
   objectChild = pirDoc.createElement(setName)
   sql = """select id from rs_%s ot where enterer_id = 1 and
   id not in (select ot.id from rs_person_story_photo_rel psp, rs_%s ot 
   where %s_id = %s and %s_id <> 0 and ot.id = psp.%s_id) order by %s desc""" % \
         (setType,setType,objectType,objectId,setType,setType,orderBy)
   Common.addXMLValue(objects,"sql",sql)
   cursor.execute("""select id from rs_%s ot where enterer_id = 1 and
   id not in (select ot.id from rs_person_story_photo_rel psp, rs_%s ot 
   where %s_id = %s and %s_id <> 0 and ot.id = psp.%s_id)order by %s desc""" % \
         (setType,setType,objectType,objectId,setType,setType,orderBy))
   fetchall = cursor.fetchall();
   rowCount = cursor.rowcount
   for row in fetchall:
      globals()[setType+"Ele"](objectChild,row[0],cursor)
   objects.appendChild(objectChild)
def personEle(personEle,personId,cursor):
   sql = "select p.id,fname,mname,lname,gender,date_format(b_date,'%%m/%%d/%%Y'), \
      b_date,address,city,state,country,zipcode,location_note \
      from rs_person p where p.id = %s" % personId
   cursor.execute(sql)
   row = cursor.fetchone();
   if (row):
      ele = pirDoc.createElement("person")
      personEle.appendChild(ele)
      ele.setAttribute("object_id", str(row[0]))
      Common.addXMLValue(ele,"object_id",str(row[0]))
      Common.addXMLValue(ele,"data",str(row[0]))
      Common.addXMLValue(ele,"label",str(row[3]+", "+row[1]+" "+row[2]))
      Common.addXMLValue(ele,"name",str(row[3]+", "+row[1]+" "+row[2]))
      Common.addXMLValue(ele,"fname",str(row[1]))
      Common.addXMLValue(ele,"mname",str(row[2]))
      Common.addXMLValue(ele,"lname",str(row[3]))
      Common.addXMLValue(ele,"gender",str(row[4]))
      if (row[6]):
         Common.addXMLValue(ele,"b_date",str(row[5]))
      else:
         Common.addXMLValue(ele,"b_date","")
      printLocation(row[7],row[8],row[9],row[10],row[11],row[12],ele)
      spouseInfo = Common.getSpouseInfo(cursor,personId)
      if (spouseInfo):
         spouseEle = pirDoc.createElement("spouse")
         ele.appendChild(spouseEle)
         Common.addXMLValue(spouseEle,"spouse_id",str(spouseInfo[1]))
         Common.addXMLValue(spouseEle,"spouse_date",str(spouseInfo[5]))
         Common.addXMLValue(spouseEle,"spouse_info",str(spouseInfo[4]+", "+ \
                     spouseInfo[2]+ " "+spouseInfo[3]+" - "+spouseInfo[5]))
      return ele
def storyEle(storyEle,storyId,cursor):
   sql = """select id,title,story_text,date_format(starts_on,'%%m/%%d/%%Y'), 
               date_format(ends_on,'%%m/%%d/%%Y'),
                address,city,state,country,zipcode,
                location_note from rs_story where id = %s""" % (storyId)
   cursor.execute(sql)
   row = cursor.fetchone();
   if (row):
      ele = pirDoc.createElement("story")
      storyEle.appendChild(ele)
      Common.addXMLValue(ele,"data",str(row[0]))
      Common.addXMLValue(ele,"label",str(row[1]))
      ele.setAttribute("object_id", str(row[0]))
      Common.addXMLValue(ele,"object_id",str(row[0]))
      Common.addXMLValue(ele,"title",str(row[1]))
      Common.addXMLValue(ele,"title_html",_mysql.escape_string(str(row[1])))
      Common.addXMLValue(ele,"story_text",str(row[2]))
      if row[3]:
         starts_on = str(row[3])
      else:
         starts_on = "00/00/0000"
      if row[4]:
         ends_on = str(row[4])
      else:
         ends_on = "00/00/0000"
      Common.addXMLValue(ele,"starts_on",starts_on)
      Common.addXMLValue(ele,"ends_on",ends_on)
      printLocation(row[5],row[6],row[7],row[8],row[9], row[10],ele)
def photoEle(photoEle,photoId,cursor):
   sql = """select id,file_name, display_name, date_format(date_taken,'%%m/%%d/%%Y'),
         address,city,state,country,zipcode,location_note, comments
         from rs_photo where id = %s""" % (photoId);
   cursor.execute(sql)
   row = cursor.fetchone();
   if (row):
      ele = pirDoc.createElement("photo")
      photoEle.appendChild(ele)
      eleChild = pirDoc.createElement("data")
      eleChild.appendChild(pirDoc.createTextNode(str(row[0])))
      ele.appendChild(eleChild)
      ele.setAttribute("object_id", str(row[0]))
      Common.addXMLValue(ele,"object_id",str(row[0]))
      # photosURL = "http://www.ripplesphere.com/rs3/photom/"
      photosURL = "http://thesystem.atwebpages.com/pir/rs/photom/"
      Common.addXMLValue(ele,"source",photosURL+"thumbnails/"+str(row[1]))
      Common.addXMLValue(ele,"source_regular",photosURL+str(row[1]))
      Common.addXMLValue(ele,"title",str(row[2]))
      Common.addXMLValue(ele,"dateTaken",str(row[3]))
      printLocation(row[4],row[5],row[6],row[7],row[8],row[9],ele)
      Common.addXMLValue(ele,"comments",str(row[10]))
def printLocation(pAddress_l1,pCity,pState,pCountry,pZipcode,pLocationNote,ele):
   address_l1=city=state=country=zipcode=location_note = ""
   if (pAddress_l1):
      address_l1 = pAddress_l1
   if (pCity):
      city = pCity
   if (pState):
      state = pState
   if (pCountry):
      country = pCountry
   if (pZipcode):
      zipcode = pZipcode
   if (pLocationNote):
      location_note = pLocationNote
   Common.addXMLValue(ele,"address_l1",address_l1)
   Common.addXMLValue(ele,"address_l2",city+" "+state+" "+country+" "+zipcode)
   Common.addXMLValue(ele,"city",city)
   Common.addXMLValue(ele,"state",state)
   Common.addXMLValue(ele,"country",country)
   Common.addXMLValue(ele,"zipcode",zipcode)
   Common.addXMLValue(ele,"location_note",location_note)

