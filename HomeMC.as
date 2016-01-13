package rs.pir.ScreenMovieClips{
	
	import flash.display.MovieClip
	import flash.net.*
	import flash.events.*
	import fl.data.DataProvider
	import fl.controls.dataGridClasses.DataGridColumn
	import rs.pir.Common.StaticClass
	import rs.pir.Common.ServerComm

	public class HomeMC extends MovieClip {
		
		private var childMC:MovieClip
		private var serverComm:ServerComm = new ServerComm()
		
		public function HomeMC():void {
			var dgc:DataGridColumn=new DataGridColumn("name")
			dgc.headerText="Persons"
			dgc.width=200
//		    dgc.sortableColumns = true
			personDG.addColumn(dgc)
			var name_dgc:DataGridColumn=new DataGridColumn("title")
			name_dgc.headerText="Stories"
			name_dgc.width=30
			storyDG.addColumn(name_dgc)
		}
		public function initialize() {
			serverComm.rsDocument = <rsDocument><pirElement></pirElement></rsDocument>
			serverComm.rsDocument.pirElement.screenName = "rotational"
			serverComm.rsDocument.pirElement.selection = <selection/>
			serverComm.rsDocument.pirElement.selection.objects += <objects><quanity>one</quanity></objects>
			serverComm.rsDocument.pirElement.selection.objects[0].@type = StaticClass.objectType
			serverComm.rsDocument.pirElement.selection.objects[0].object_id = StaticClass.objectId
			serverComm.rsDocument.pirElement.selection.objects += <objects type="person"><quanity>many</quanity><size>all</size></objects>
			serverComm.rsDocument.pirElement.selection.objects += <objects type="story"><quanity>many</quanity><size>all</size></objects>
			serverComm.rsDocument.pirElement.selection.objects += <objects type="photo"><quanity>many</quanity><size>all</size></objects>
			serverComm.toServer(returnedInitialDataSet)
		}
		private function returnedInitialDataSet() {
			if (StaticClass.objectType == "person") {
				childMC = new PersonViewMC()
				childMC.spouse_dt.text = ""
				childMC.spouseBtn.visible = false
				childMC.populateXML(serverComm.rsDocument.pirElement.person)
			} else if (StaticClass.objectType == "story") {
				childMC = new StoryViewMC()
				childMC.populateXML(serverComm.rsDocument.pirElement.story)
			} else if (StaticClass.objectType == "photo") {
				childMC = new PhotoViewMC()
				childMC.populateXML(serverComm.rsDocument.pirElement.photo)
			}
			childMC.x = 175
			childMC.y = 78
			addChild(childMC)
			personDG.dataProvider = new DataProvider(serverComm.rsDocument.pirElement.persons[0])
			var count:Number = 0, item
			for each (item in serverComm.rsDocument.pirElement.persons[0].person.name) { 
				serverComm.rsDocument.pirElement.persons[0].person[count].name = decodeURIComponent(item)
				if (StaticClass.objectType == "person" && StaticClass.objectId == serverComm.rsDocument.pirElement.persons[0].person[count].object_id) {
					personDG.selectedIndex = count
				}
				count++
			} 
			storyDG.dataProvider = new DataProvider(serverComm.rsDocument.pirElement.stories[0])
			count = 0
			for each (item in serverComm.rsDocument.pirElement.stories[0].story.title) { 
				serverComm.rsDocument.pirElement.stories[0].story[count].title = decodeURIComponent(item)
				if (StaticClass.objectType == "story" && StaticClass.objectId == serverComm.rsDocument.pirElement.stories[0].story[count].object_id) {
					storyDG.selectedIndex = count
				}
				count++
			} 
			photoTL.dataProvider = new DataProvider(serverComm.rsDocument.pirElement.photos[0])
			count = 0
			for each (item in serverComm.rsDocument.pirElement.photos[0].photo.title) { 
				serverComm.rsDocument.pirElement.photos[0].photo[count].title = decodeURIComponent(item)
				if (StaticClass.objectType == "photo" && StaticClass.objectId == serverComm.rsDocument.pirElement.photos[0].photo[count].object_id) {
					photoTL.selectedIndex = count
				}
				count++
			} 
			tabbedBtn.addEventListener(MouseEvent.CLICK,changeToSide)
			relationalBtn.addEventListener(MouseEvent.CLICK,changeToSide)
			rotationalBtn.addEventListener(MouseEvent.CLICK,changeToSide)
			addPersonBtn.addEventListener(MouseEvent.CLICK,addObjectHandler)
			addStoryBtn.addEventListener(MouseEvent.CLICK,addObjectHandler)
			addPhotoBtn.addEventListener(MouseEvent.CLICK,addObjectHandler)
			personDG.addEventListener(Event.CHANGE, changeObjectHandler)
			storyDG.addEventListener(Event.CHANGE, changeObjectHandler)
			photoTL.addEventListener(Event.CHANGE, changeObjectHandler)
		}
	 	public function changeToSide(event:Event) {
			if (event.currentTarget.name == "tabbedBtn") {
				StaticClass.changeSides("tabbed")
			} else if (event.currentTarget.name == "relationalBtn") {
				StaticClass.changeSides("relational")
			} else if (event.currentTarget.name == "rotationalBtn") {
				StaticClass.changeSides("rotational")
			}
		}
		public function changeObjectHandler(event:Event):void {
			removeChild(childMC)
			if (event.currentTarget.name == "personDG") {
				StaticClass.objectType = "person"
				childMC = new PersonViewMC()
				childMC.spouse_dt.text = ""
				childMC.spouseBtn.visible = false
			} else if (event.currentTarget.name == "storyDG") {
				StaticClass.objectType = "story"
				childMC = new StoryViewMC()
				personDG.selectedIndex = -1
			} else if (event.currentTarget.name == "photoTL") {
				StaticClass.objectType = "photo"
				childMC = new PhotoViewMC()
			}
			childMC.populateObject(event.currentTarget.selectedItem)
			StaticClass.objectId = event.currentTarget.selectedItem.object_id
			childMC.x = 175
			childMC.y = 78
			addChild(childMC)
		}
		private function addObjectHandler(event:MouseEvent):void {
			removeChild(childMC)
			if (event.target.name == "addPersonBtn") {
				childMC = new PersonAddMC()
				childMC.cancelBtn.addEventListener(MouseEvent.CLICK,cancelAddChildMC)
				childMC.commitBtn.addEventListener(MouseEvent.CLICK,addPersonBtnClickHandler)
			} else if (event.target.name == "addStoryBtn") {
				childMC = new StoryAddMC()
				childMC.cancelBtn.addEventListener(MouseEvent.CLICK,cancelAddChildMC)
				childMC.commitBtn.addEventListener(MouseEvent.CLICK,addStoryBtnClickHandler)
			} else if (event.target.name == "addPhotoBtn") {
				childMC = new PhotoAddMC()
				childMC.prepareForUpload()
				childMC.fileRef.addEventListener(Event.SELECT, selectHandler)
            	childMC.fileRef.addEventListener(Event.CANCEL, cancelAddChildMC);
//			 	childMC.cancelBtn.addEventListener(MouseEvent.CLICK,cancelAddChildMC)
			}
			childMC.x = 176
			childMC.y = 78
			addChild(childMC)
        }
		public function cancelAddChildMC(event:Event):void {
			removeChild(childMC)
			var objectObject:Object
			if (StaticClass.objectType == "person") {
				childMC = new PersonViewMC()
				childMC.spouse_dt.text = ""
				childMC.spouseBtn.visible = false
				objectObject = personDG.selectedItem
			} else if (event.currentTarget.name == "story") {
				childMC = new StoryViewMC()
				objectObject = storyDG.selectedItem
			} else if (event.currentTarget.name == "photo") {
				childMC = new PhotoViewMC()
				objectObject = photoTL.selectedItem
			}
			childMC.populateObject(objectObject)
			childMC.x = 175
			childMC.y = 78
			addChild(childMC)
		}
		private function addPersonBtnClickHandler(event:MouseEvent):void {
			serverComm=new ServerComm  
			serverComm.rsDocument.pirElement.screenName = "rotational"
			serverComm.rsDocument.pirElement.action = <action/>
			serverComm.rsDocument.pirElement.action.object_type = "person"
			serverComm.rsDocument.pirElement.action.action_type = "add"
			childMC.populatePIRDocument(serverComm.rsDocument)
			serverComm.rsDocument.pirElement.selection = <selection/>
			serverComm.rsDocument.pirElement.selection.objects += <objects type="person"><quanity>one</quanity></objects>
			serverComm.toServer(returnedFromPersonAdded)
        }
		private function returnedFromPersonAdded():void {
			StaticClass.objectType = "person"
			StaticClass.objectId = serverComm.rsDocument.pirElement.person.object_id
			StaticClass.changeSides("enter")
		}
		private function addStoryBtnClickHandler(event:MouseEvent):void {
			serverComm=new ServerComm  
			serverComm.rsDocument.pirElement.screenName = "rotational"
			serverComm.rsDocument.pirElement.action = <action/>
			serverComm.rsDocument.pirElement.action.object_type = "story"
			serverComm.rsDocument.pirElement.action.action_type = "add"
			childMC.populatePIRDocument(serverComm.rsDocument)
			serverComm.rsDocument.pirElement.selection = <selection/>
			serverComm.rsDocument.pirElement.selection.objects += <objects type="story"><quanity>one</quanity></objects>
			serverComm.toServer(returnedFromStoryAdded)
        }
		private function returnedFromStoryAdded():void {
			StaticClass.objectType = "story"
			StaticClass.objectId = serverComm.rsDocument.pirElement.story.object_id
			StaticClass.changeSides("enter")
		}
		private function selectHandler(event:Event):void {
			childMC.fileRef=FileReference(event.target)
			childMC.fileRef.upload(childMC.uploadURL)
			childMC.imageUploadPB.source=childMC.fileRef
			childMC.fileRef.addEventListener(DataEvent.UPLOAD_COMPLETE_DATA, uploadCompleteDataHandler)
		}
        private function uploadCompleteDataHandler(event:Event):void {
//			removeChild(functionalityMC)
//			functionalityMC = new PhotoScreenMC()
//			functionalityMC.x = 125
//			functionalityMC.y = 78
//			addChild(functionalityMC)
//			functionalityMC.loadAfterAddScreen(event["data"])
			StaticClass.objectType = "photo"
			StaticClass.objectId = event["data"]
			StaticClass.changeSides("enter")
        }
	}
}
