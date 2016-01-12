import xml.dom.minidom
#import MySQLdb
import psycopg2
import Common
doc = xml.dom.minidom.Document()
userId = 1
pirEle  = xml.dom.minidom.Document()
cursor = 0
def relational(user_id,pirEleIn,cursorIn):
   global userId
   global pirEle
   global cursor
   userId = user_id
   pirEle = pirEleIn
   cursor = cursorIn
   if (pirEle.getElementsByTagName("request")[0].childNodes[0].nodeValue=="fromListView"):
      objectType = pirEle.getElementsByTagName("listItemType")[0].childNodes[0].nodeValue
      objectId = pirEle.getElementsByTagName("listItemId")[0].childNodes[0].nodeValue
      cursor.execute("""delete from rs_nav_path where user_id = %s""" % (userId))
      cursor.execute("""update rs_person set depth = 0 where id = %s""" % (userId))
      objectType = objectType.lower()
      modifyRSNavPath("insert",objectType,objectId,0)
      screenObjectSet()
   elif (pirEle.getElementsByTagName("request")[0].childNodes[0].nodeValue=="changedReasonObject"):
      cursor.execute("""select depth from rs_person where id = %s""" % (userId))
      depth = cursor.fetchone()[0]
      objectType,objectId = changedSectionObject(depth+2)
      forwardInNavPathChild = doc.createElement("foundForwardObject")
      forwardInNavPathChild.appendChild(doc.createTextNode(str(
                        checkForRelation(objectType,objectId,depth+3))))
      pirEle.appendChild(forwardInNavPathChild)
   elif (pirEle.getElementsByTagName("request")[0].childNodes[0].nodeValue=="changedManyObject"):
      cursor.execute("""select depth from rs_person where id = %s""" % (userId))
      depth = cursor.fetchone()[0]
      objectType,objectId = changedSectionObject(depth+1)
      if (checkForRelation(objectType,objectId,depth+2)):
         objectType,objectId = navRowSet("reason",depth+2)
         forwardInNavPathChild = doc.createElement("foundForwardObject")
         forwardInNavPathChild.appendChild(doc.createTextNode(str(
                                    checkForRelation(objectType,objectId,depth+3))))
         pirEle.appendChild(forwardInNavPathChild)
   elif (pirEle.getElementsByTagName("request")[0].childNodes[0].nodeValue=="forward"):
      cursor.execute("""select depth from rs_person where id = %s""" % (userId))
      depth = cursor.fetchone()[0]
      cursor.execute("""update rs_person set depth = %s where id = %s""" % (depth+1,userId))
      screenObjectSet()
   elif (pirEle.getElementsByTagName("request")[0].childNodes[0].nodeValue=="back"):
      cursor.execute("""select depth from rs_person where id = %s""" % (userId))
      depth = cursor.fetchone()[0]
      cursor.execute("""update rs_person set depth = %s where id = %s""" % (depth-1,userId))
      screenObjectSet()
def screenObjectSet():
   focusChild = doc.createElement("focus")
   pirEle.appendChild(focusChild)
   cursor.execute("""select np.object_type,np.object_id,p.depth from rs_person p,rs_nav_path
         np where p.id=%s and p.depth=np.depth and np.user_id=p.id""" % (userId))
   objectType,objectId,depth = cursor.fetchone()
   if (objectType=="person"):
      eleChild=doc.createElement("persons")
      Common.personEle(eleChild,objectId,cursor)
   elif (objectType=="story"):
      eleChild=doc.createElement("stories")
      Common.storyEle(eleChild,objectId,cursor)
   elif (objectType=="photo"):
      eleChild = doc.createElement("photos")
      Common.photoEle(eleChild,objectId,cursor)
   focusChild.appendChild(eleChild)
   eleChild = doc.createElement("objectType")
   eleChild.appendChild(doc.createTextNode(str(objectType)))
   focusChild.appendChild(eleChild)
   canBackInNavPath = doc.createElement("canBackInNavPath")
   canBackInNavPath.appendChild(doc.createTextNode(str(depth)))
   pirEle.appendChild(canBackInNavPath)
   objectSet = nextDepthObjectSet(objectType,objectId,depth+1,"many")  
   if (objectSet[0]):
      selTypeChild = doc.createElement("manySetExists")
      selTypeChild.appendChild(doc.createTextNode(str(1)))
      pirEle.appendChild(selTypeChild)
      objectSet = nextDepthObjectSet(objectSet[1],objectSet[2],depth+2,"reason")
      if (objectSet[0]):
         selTypeChild = doc.createElement("reasonSetExists")
         selTypeChild.appendChild(doc.createTextNode(str(1)))
         pirEle.appendChild(selTypeChild)
         cursor.execute("""select 1 from rs_nav_path where depth=%s and user_id=%s""" \
                           % (depth+3,userId))
         if (cursor.fetchone()): 
            isForwardObjectSet = 1
         else:
            isForwardObjectSet = checkForRelation(objectSet[1],objectSet[2],depth+3)
         if (isForwardObjectSet):
            forwardInNavPathChild = doc.createElement("foundForwardObject")
            forwardInNavPathChild.appendChild(doc.createTextNode(str(1)))
            pirEle.appendChild(forwardInNavPathChild)
      else:
         setExistsChild = doc.createElement("reasonSetExists")
         setExistsChild.appendChild(doc.createTextNode(str(0)))
         pirEle.appendChild(setExistsChild)
   else:
      setExistsChild = doc.createElement("manySetExists")
      setExistsChild.appendChild(doc.createTextNode(str(0)))
      pirEle.appendChild(setExistsChild)
def modifyRSNavPath(operation,objectType,objectId,depth):
   if (operation == "insert"):
      cursor.execute("""insert into rs_nav_path (object_type,object_id,depth,user_id) values
                        ("%s",%s,%s,%s)""" % (objectType,objectId,depth,userId))
   elif (operation == "update"):
      cursor.execute("""update rs_nav_path set object_type = "%s", object_id = %s 
               where depth = %s and user_id = %s""" % (objectType,objectId,depth,userId))
def changedSectionObject(sectionDepth):
   objectType = pirEle.getElementsByTagName("listItemType")[0].childNodes[0].nodeValue
   objectId = pirEle.getElementsByTagName("listItemId")[0].childNodes[0].nodeValue
   modifyRSNavPath("update",objectType,objectId,sectionDepth)
   cursor.execute("""select object_type,object_id from rs_nav_path where depth = %s
            and user_id = %s""" % (sectionDepth-1,userId))
   upObjectType,upObjectId = cursor.fetchone()
   cursor.execute("""update rs_display_preferences set pref_type = "%s",pref_id = %s where 
            object_type = "%s" and object_id = %s and selected = 1
            and user_id = %s""" % (objectType,objectId,upObjectType,upObjectId,userId))
   cursor.execute("""delete from rs_nav_path where user_id = %s and depth > %s""" \
          % (userId,int(sectionDepth)))
   return objectType,objectId
def nextDepthObjectSet(objectType,objectId,navPathDepth,depthName):
   cursor.execute("""select id from rs_nav_path where depth=%s and user_id=%s""" \
                     %(navPathDepth,userId))
   navRowObject=cursor.fetchone()
   if (navRowObject): 
      objectType,objectId = navRowSet(depthName,navPathDepth)
      return 1,objectType,objectId
   else:
      if (checkForRelation(objectType,objectId,navPathDepth)):
         objectType,objectId = navRowSet(depthName,navPathDepth)
         return 1,objectType,objectId
   return 0,0,0
def navRowSet(eleName,depth):
   groupChild = doc.createElement(eleName)
   pirEle.appendChild(groupChild)
   cursor.execute("""select object_type,object_id from rs_nav_path where depth = %s""" % (depth))
   objectType,objectId = cursor.fetchone()
   selTypeChild = doc.createElement("selectedType")
   selTypeChild.appendChild(doc.createTextNode(str(objectType)))
   groupChild.appendChild(selTypeChild)
   selIdChild = doc.createElement("selectedId")
   selIdChild.appendChild(doc.createTextNode(str(objectId)))
   groupChild.appendChild(selIdChild)
   cursor.execute("""select object_type,object_id from rs_nav_path where depth = %s""" % (depth-1))
   parentType,parentId = cursor.fetchone()
   personsChild = doc.createElement("persons")
   cursor.execute("""select person_id from rs_person_story_photo_rel psp, rs_person typeTable 
                     where %s_id = %s and person_id <> 0 
                     and typeTable.id = psp.person_id order by b_date desc""" \
                           % (parentType,parentId))
   fetchall = cursor.fetchall();
   for row in fetchall:
      if (parentType != "person" and parentId != row[0]):
         Common.personEle(personsChild,row[0],cursor)
   groupChild.appendChild(personsChild)
   eleChild = doc.createElement("stories")
   cursor.execute("""select story_id from rs_person_story_photo_rel psp, rs_story typeTable 
                     where %s_id = %s and story_id <> 0 and 
                     typeTable.id = psp.story_id order by starts_on desc""" % (parentType,parentId))
   fetchall = cursor.fetchall();
   for row in fetchall:
      if (parentType != "story" and parentId != row[0]):
         Common.storyEle(eleChild,row[0],cursor)
   groupChild.appendChild(eleChild)
   eleChild = doc.createElement("photos")
   cursor.execute("""select photo_id from rs_person_story_photo_rel psp, rs_photo typeTable 
                     where %s_id = %s and photo_id <> 0 and 
                     typeTable.id = psp.photo_id order by date_taken desc""" \
                           % (parentType,parentId))
   fetchall = cursor.fetchall();
   for row in fetchall:
      if (parentType != "photo" and parentId != row[0]):
         Common.photoEle(eleChild,row[0],cursor)
   groupChild.appendChild(eleChild)
   return objectType,objectId
def addDisplayPrefAndNavPathRow(objectType,objectId,pref_type,pref_id,depth):
   cursor.execute("""insert into rs_display_preferences (user_id,object_type,object_id,selected, 
                     pref_type,pref_id) values (%s,"%s",%s,1,"%s",%s)""" \
                           % (userId,objectType,objectId,pref_type,pref_id))
   modifyRSNavPath("insert",pref_type,pref_id,depth)
   return 1
def checkForRelation(objectType,objectId,depth):
   cursor.execute("""select pref_type,pref_id from rs_display_preferences 
                     where object_type = "%s" and object_id = %s and 
                     user_id = %s""" % (objectType,objectId,userId))
   displayPreference = cursor.fetchone()
   if (displayPreference):
      modifyRSNavPath("insert",displayPreference[0],displayPreference[1],depth)
      return 1
   cursor.execute("""select photo_id from rs_person_story_photo_rel psp, rs_photo typeTable 
                     where %s_id = %s and photo_id <> 0 and 
                     typeTable.id = psp.photo_id order by date_taken desc""" \
                           % (objectType, objectId))
   fetchall = cursor.fetchall();
   for row in fetchall:
      if (objectType != "photo" and objectId != row[0]):
         return addDisplayPrefAndNavPathRow(objectType,objectId,"photo",row[0],depth)
   cursor.execute("""select story_id from rs_person_story_photo_rel psp, rs_story typeTable 
                     where %s_id = %s and story_id <> 0 and 
                     typeTable.id = psp.story_id order by starts_on desc""" \
                           % (objectType, objectId))
   fetchall = cursor.fetchall();
   for row in fetchall:
       if (objectType != "story" and objectId != row[0]):
         return addDisplayPrefAndNavPathRow(objectType,objectId,"story",row[0],depth)
   cursor.execute("""select person_id from rs_person_story_photo_rel psp, rs_person typeTable 
                     where %s_id = %s and person_id <> 0 and 
                     typeTable.id = psp.person_id order by b_date desc""" \
                           % (objectType, objectId))
   fetchall = cursor.fetchall();
   for row in fetchall:
      if (objectType != "person" and objectId != row[0]):
         return addDisplayPrefAndNavPathRow(objectType,objectId,"person",row[0],depth)
   return 0        
