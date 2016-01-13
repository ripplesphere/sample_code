package rs.pir.RelationView{
	import flash.display.MovieClip;
	import fl.controls.dataGridClasses.DataGridColumn;
	import fl.data.DataProvider;
	import flash.events.Event;
	import flash.events.MouseEvent;
	import flash.net.*;
	import fl.transitions.Tween;
	import fl.transitions.TweenEvent
	import fl.transitions.easing.*;
	import rs.pir.Common.StaticClass
	import rs.pir.Common.ServerComm
	
	public class RelationalMC extends MovieClip {
		private var serverComm:ServerComm = new ServerComm()
		public var focusElementMC:MovieClip
		public var manyObjectTypeMC:MovieClip
		public var reasonObjectTypeMC:MovieClip
		var anExtraObjectMC:MovieClip
		var aSecondExtraObjectMC:MovieClip
		var personCBExtraObjectMC:MovieClip
		var storyCBExtraObjectMC:MovieClip
		var photoTLExtraObjectMC:MovieClip
		var manySwitchToBtnsMC:MovieClip
		public var listItemType
		public var listItemId
		public var alphaTween:Tween
		var navigationDirection:String
		var firstRun:Number = 1
		var item
		public var relationTween:Tween

		public function RelationalMC():void {
			backBtn.addEventListener(MouseEvent.CLICK,navigationBtnsHandler);
			forwardBtn.addEventListener(MouseEvent.CLICK,navigationBtnsHandler);
			manyListGroupMC.personCB.addEventListener(Event.CHANGE, manyChangeHandler);
			manyListGroupMC.storyCB.addEventListener(Event.CHANGE, manyChangeHandler);
			manyListGroupMC.photoTL.addEventListener(Event.CHANGE, manyChangeHandler);
			reasonListGroupMC.personCB.addEventListener(Event.CHANGE, reasonChangeHandler);
			reasonListGroupMC.storyCB.addEventListener(Event.CHANGE, reasonChangeHandler);
			reasonListGroupMC.photoTL.addEventListener(Event.CHANGE, reasonChangeHandler);
			manyListGroupMC.alpha = 0
			reasonListGroupMC.alpha = 0
		}
		public function initialize() {
//			serverComm.rsDocument = <serverComm.rsDocument><pirElement>
//								<screenName>relationView</screenName>
//   							</pirElement></serverComm.rsDocument>
//			serverComm.rsDocument.pirElement.request = whereFrom
//			if (whereFrom == "fromListView") {
//				serverComm.rsDocument.pirElement.selectedListItem.listItemType = listItemType
//				serverComm.rsDocument.pirElement.selectedListItem.listItemId = listItemId
//			}
//			wisdom.displayChange(serverComm.rsDocument,returnedFocusFromServer);
			serverComm = new ServerComm()
			serverComm.rsDocument = <rsDocument><pirElement></pirElement></rsDocument>
			serverComm.rsDocument.pirElement.screenName = "relational"
			serverComm.rsDocument.pirElement.request = "fromListView"
			serverComm.rsDocument.pirElement.selectedListItem.listItemType = StaticClass.objectType
			serverComm.rsDocument.pirElement.selectedListItem.listItemId = StaticClass.objectId
			serverComm.toServer(returnedFocusFromServer)
		}
		protected function returnedFocusFromServer():void {
			relationTween = new Tween(this, "alpha", Regular.easeInOut, 0, 1, 1, true);
			checkNavigationBtns(serverComm.rsDocument.pirElement.canBackInNavPath,serverComm.rsDocument.pirElement.foundForwardObject)
			if (firstRun) {
				if (serverComm.rsDocument.pirElement.focus.objectType=="person") {
					focusElementMC = new PersonViewMC()
					focusElementMC.populateXML(serverComm.rsDocument.pirElement.focus.persons[0].person[0])
				} else if (serverComm.rsDocument.pirElement.focus.objectType == "story") {
					focusElementMC = new StoryViewMC()
					focusElementMC.populateXML(serverComm.rsDocument.pirElement.focus.stories[0].story[0])
				} else if (serverComm.rsDocument.pirElement.focus.objectType == "photo") {
					focusElementMC = new PhotoViewMC()
					focusElementMC.populateXML(serverComm.rsDocument.pirElement.focus.photos[0].photo[0])
				}
				focusElementMC.x = 70
				focusElementMC.y = 131
				addChildAt(focusElementMC,0)
			}
			focusElementMC.type = new String(serverComm.rsDocument.pirElement.focus.objectType)
			if (serverComm.rsDocument.pirElement.manySetExists == 1) {
				returnedManyFromServer()
			} else {
				manySeeInListViewBtn.enabled = false
				reasonSeeInListViewBtn.enabled = false
			}
		}
		protected function returnedManyFromServer():void {
			if (serverComm.rsDocument.pirElement.foundRelative == 0) {
				manySeeInListViewBtn.enabled = false
				reasonSeeInListViewBtn.enabled = false
				return
			}
			manyListGroupMC.personCB.dataProvider = new DataProvider(serverComm.rsDocument.pirElement.many.persons[0])
			manyListGroupMC.storyCB.dataProvider = new DataProvider(serverComm.rsDocument.pirElement.many.stories[0])
			manyListGroupMC.photoTL.dataProvider = new DataProvider(serverComm.rsDocument.pirElement.many.photos[0])
			manyListGroupMC.personCB.addItemAt( { label: "Select", data:0 },0 );
			manyListGroupMC.storyCB.addItemAt( { label: "Select", data:0 },0 );
			var listIndex = 1
			var objectId = serverComm.rsDocument.pirElement.many.selectedId
			if (serverComm.rsDocument.pirElement.many.selectedType == "person") {
				for each (item in serverComm.rsDocument.pirElement.many.persons[0].person) 
				{ 
					if (item.@id == objectId) {
						break
					}
					listIndex++
				} 
				manyListGroupMC.personCB.selectedIndex = listIndex
			} else if (serverComm.rsDocument.pirElement.many.selectedType == "story") {
				for each (item in serverComm.rsDocument.pirElement.many.stories[0].story) 
				{ 
					if (item.@id == objectId) {
						break
					}
					listIndex++
				} 
				manyListGroupMC.storyCB.selectedIndex = listIndex
			} else if (serverComm.rsDocument.pirElement.many.selectedType == "photo") {
				for each (item in serverComm.rsDocument.pirElement.many.photos[0].photo) 
				{ 
					if (item.@id == objectId) {
						break
					}
					listIndex++
				} 
				manyListGroupMC.photoTL.selectedIndex = listIndex-1
			}
			if (firstRun) {
				if (serverComm.rsDocument.pirElement.many.selectedType == "person") {
					manyObjectTypeMC = new PersonViewMC()
					manyObjectTypeMC.populateXML(serverComm.rsDocument.pirElement.many.persons[0].person[listIndex-1])
				} else if (serverComm.rsDocument.pirElement.many.selectedType == "story") {
					manyObjectTypeMC = new StoryViewMC()
					manyObjectTypeMC.populateXML(serverComm.rsDocument.pirElement.many.stories[0].story[listIndex-1])
				} else if (serverComm.rsDocument.pirElement.many.selectedType == "photo") {
					manyObjectTypeMC = new PhotoViewMC()
					manyObjectTypeMC.populateXML(serverComm.rsDocument.pirElement.many.photos[0].photo[listIndex-1])
				}
				manyObjectTypeMC.x = 490
				manyObjectTypeMC.y = 131
				addChildAt(manyObjectTypeMC,0)
				manyObjectTypeMC.alphaTween = new Tween(manyObjectTypeMC, "alpha", Regular.easeIn, 0, 1, 1, true);
				manyListGroupMC.alphaTween = new Tween(manyListGroupMC, "alpha", Regular.easeIn, 0, 1, 1, true);
			}
			if (serverComm.rsDocument.pirElement.reasonSetExists == 1) {
				returnedReasonFromServer()
			} else {
				reasonSeeInListViewBtn.enabled = false
			}
		}
		protected function returnedReasonFromServer():void {
			if (serverComm.rsDocument.pirElement.reasonSetExists == 0) {
				reasonSeeInListViewBtn.enabled = false
				return
			}
			reasonListGroupMC.personCB.dataProvider = new DataProvider(serverComm.rsDocument.pirElement.reason.persons[0])
			reasonListGroupMC.storyCB.dataProvider = new DataProvider(serverComm.rsDocument.pirElement.reason.stories[0])
			reasonListGroupMC.photoTL.dataProvider = new DataProvider(serverComm.rsDocument.pirElement.reason.photos[0])
//			reasonListGroupMC.personCB.addItemAt( { label: "Select", data:0 },0 );
//			reasonListGroupMC.storyCB.addItemAt( { label: "Select", data:0 },0 );
			var listIndex = 1
			var objectId = serverComm.rsDocument.pirElement.reason.selectedId
			var item
			if (serverComm.rsDocument.pirElement.reason.selectedType == "person") {
				for each (item in serverComm.rsDocument.pirElement.reason.persons[0].person) 
				{ 
					if (item.@id == objectId) {
						break
					}
					listIndex++
				} 
				reasonListGroupMC.personCB.selectedIndex = listIndex
			} else if (serverComm.rsDocument.pirElement.reason.selectedType == "story") {
				for each (item in serverComm.rsDocument.pirElement.reason.stories[0].story) 
				{ 
					if (item.@id == objectId) {
						break
					}
					listIndex++
				} 
				reasonListGroupMC.storyCB.selectedIndex = listIndex
			} else if (serverComm.rsDocument.pirElement.reason.selectedType == "photo") {
				for each (item in serverComm.rsDocument.pirElement.reason.photos[0].photo) 
				{ 
					if (item.@id == objectId) {
						break
					}
					listIndex++
				} 
				reasonListGroupMC.photoTL.selectedIndex = listIndex-1
			}
			if (firstRun) {
				if (serverComm.rsDocument.pirElement.reason.selectedType == "person") {
					reasonObjectTypeMC = new PersonViewMC()
					reasonObjectTypeMC.populateXML(serverComm.rsDocument.pirElement.reason.persons[0].person[listIndex-1])
				} else if (serverComm.rsDocument.pirElement.reason.selectedType == "story") {
					reasonObjectTypeMC = new StoryViewMC()
					reasonObjectTypeMC.populateXML(serverComm.rsDocument.pirElement.reason.stories[0].story[listIndex-1])
				} else if (serverComm.rsDocument.pirElement.reason.selectedType == "photo") {
					reasonObjectTypeMC = new PhotoViewMC()
					reasonObjectTypeMC.populateXML(serverComm.rsDocument.pirElement.reason.photos[0].photo[listIndex-1])
				}
				reasonListGroupMC.personCB.addItemAt( { label: "Select", data:0 },0 );
				reasonListGroupMC.storyCB.addItemAt( { label: "Select", data:0 },0 );
				reasonObjectTypeMC.x = 930
				reasonObjectTypeMC.y = 131
				addChildAt(reasonObjectTypeMC,0)
				reasonObjectTypeMC.alphaTween = new Tween(reasonObjectTypeMC, "alpha", Regular.easeIn, 0, 1, 1, true);
				reasonListGroupMC.alphaTween = new Tween(reasonListGroupMC, "alpha", Regular.easeIn, 0, 1, 1, true);
				firstRun = 0
			}
		}
		private function manyChangeHandler(event:Event):void {
			if (event.target.selectedIndex == 0 && event.target.name != "photoTL") {
				return
			}
			aSecondExtraObjectMC = manyObjectTypeMC
			aSecondExtraObjectMC.alphaTween = new Tween(aSecondExtraObjectMC, "alpha", Regular.easeIn, 1, 0, 1, true);
			aSecondExtraObjectMC.alphaTween.addEventListener(TweenEvent.MOTION_FINISH,manyChangedManyAlphaDone)
			serverComm.rsDocument = <serverComm.rsDocument><pirElement>
						<screenName>relational</screenName>
						<request>changedManyObject</request>
					</pirElement></serverComm.rsDocument>
			if (event.target.name == "personCB") {
				serverComm.rsDocument.pirElement.selectedListItem.listItemType = "person"
				manyObjectTypeMC = new PersonViewMC()
				manyObjectTypeMC.populateObject(manyListGroupMC.personCB.selectedItem)
				manyListGroupMC.storyCB.selectedIndex = -1
				manyListGroupMC.photoTL.selectedIndex = -1
			} else if (event.target.name == "storyCB") {
				serverComm.rsDocument.pirElement.selectedListItem.listItemType = "story"
				manyObjectTypeMC = new StoryViewMC()
				manyObjectTypeMC.populateObject(manyListGroupMC.storyCB.selectedItem)
				manyListGroupMC.personCB.selectedIndex = -1
				manyListGroupMC.photoTL.selectedIndex = -1
			} else if (event.target.name == "photoTL") {
			    serverComm.rsDocument.pirElement.selectedListItem.listItemType = "photo"
				manyObjectTypeMC = new PhotoViewMC()
				manyObjectTypeMC.populateDP(new DataProvider(manyListGroupMC.photoTL.selectedItems))
				manyListGroupMC.personCB.selectedIndex = -1
				manyListGroupMC.storyCB.selectedIndex = -1
			}
			serverComm.rsDocument.pirElement.selectedListItem.listItemId = event.target.selectedItem.id
			serverComm.toServer(returnedManyChangedFromServer)
//			wisdom.displayChange(serverComm.rsDocument,returnedManyChangedFromServer);
		}
		private function manyChangedManyAlphaDone(event:TweenEvent):void {
			removeChild(aSecondExtraObjectMC)
			manyObjectTypeMC.x = 490
			manyObjectTypeMC.y = 131
			addChildAt(manyObjectTypeMC,0)
			manyObjectTypeMC.alphaTween = new Tween(manyObjectTypeMC, "alpha", Regular.easeOut, 0, 1, 1, true);
		}
		protected function returnedManyChangedFromServer():void {
			anExtraObjectMC = reasonObjectTypeMC
			anExtraObjectMC.alphaTween = new Tween(anExtraObjectMC, "alpha", Regular.easeIn, 1, 0, 1, true);
			reasonListGroupMC.alphaTween = new Tween(reasonListGroupMC, "alpha", Regular.easeIn, 1, 0, 1, true);
			if (serverComm.rsDocument.pirElement.foundForwardObject == 1) {
				anExtraObjectMC.alphaTween.addEventListener(TweenEvent.MOTION_FINISH,manyChangedAlphaDone)
				forwardBtn.enabled = true
			} else {
				forwardBtn.enabled = false
			}
		}
		private function manyChangedAlphaDone(event:TweenEvent):void {
			reasonListGroupMC.personCB.dataProvider = new DataProvider(serverComm.rsDocument.pirElement.reason.persons[0])
			reasonListGroupMC.storyCB.dataProvider = new DataProvider(serverComm.rsDocument.pirElement.reason.stories[0])
			reasonListGroupMC.photoTL.dataProvider = new DataProvider(serverComm.rsDocument.pirElement.reason.photos[0])
			reasonListGroupMC.personCB.addItemAt( { label: "Select", data:0 },0 );
			reasonListGroupMC.storyCB.addItemAt( { label: "Select", data:0 },0 );
			var listIndex = 1
			var objectId = serverComm.rsDocument.pirElement.reason.selectedId
			var item
			if (serverComm.rsDocument.pirElement.reason.selectedType == "person") {
				for each (item in serverComm.rsDocument.pirElement.reason.persons[0].person) 
				{ 
					if (item.@id == objectId) {
						break
					}
					listIndex++
				} 
				reasonListGroupMC.personCB.selectedIndex = listIndex
			} else if (serverComm.rsDocument.pirElement.reason.selectedType == "story") {
				for each (item in serverComm.rsDocument.pirElement.reason.stories[0].story) 
				{ 
					if (item.@id == objectId) {
						break
					}
					listIndex++
				} 
				reasonListGroupMC.storyCB.selectedIndex = listIndex
			} else if (serverComm.rsDocument.pirElement.reason.selectedType == "photo") {
				for each (item in serverComm.rsDocument.pirElement.reason.photos[0].photo) 
				{ 
					if (item.@id == objectId) {
						break
					}
					listIndex++
				} 
				reasonListGroupMC.photoTL.selectedIndex = listIndex-1
			}
				if (serverComm.rsDocument.pirElement.reason.selectedType == "person") {
					reasonObjectTypeMC = new PersonViewMC()
					reasonObjectTypeMC.populateXML(serverComm.rsDocument.pirElement.reason.persons[0].person[listIndex-1])
				} else if (serverComm.rsDocument.pirElement.reason.selectedType == "story") {
					reasonObjectTypeMC = new StoryViewMC()
					reasonObjectTypeMC.populateXML(serverComm.rsDocument.pirElement.reason.stories[0].story[listIndex-1])
				} else if (serverComm.rsDocument.pirElement.reason.selectedType == "photo") {
					reasonObjectTypeMC = new PhotoViewMC()
					reasonObjectTypeMC.populateXML(serverComm.rsDocument.pirElement.reason.photos[0].photo[listIndex-1])
				}
			removeChild(anExtraObjectMC)
			reasonObjectTypeMC.x = 930
			reasonObjectTypeMC.y = 131
			addChildAt(reasonObjectTypeMC,0)
			reasonObjectTypeMC.alphaTween = new Tween(reasonObjectTypeMC, "alpha", Regular.easeIn, 0, 1, 1, true);
			reasonListGroupMC.alphaTween = new Tween(reasonListGroupMC, "alpha", Regular.easeIn, 0, 1, 1, true);
		}
		private function reasonChangeHandler(event:Event):void {
			if ((event.target.selectedIndex == 0 && event.target.name != "photoTL")) {
				return
			}
			anExtraObjectMC = reasonObjectTypeMC
			anExtraObjectMC.alphaTween = new Tween(anExtraObjectMC, "alpha", Regular.easeOut, 1, 0, 1, true);
			anExtraObjectMC.alphaTween.addEventListener(TweenEvent.MOTION_FINISH,reasonAlphaDone)
			serverComm.rsDocument = <serverComm.rsDocument><pirElement>
						<screenName>relational</screenName>
						<request>changedReasonObject</request>
					</pirElement></serverComm.rsDocument>
			if (event.target.name == "personCB") {
				serverComm.rsDocument.pirElement.selectedListItem.listItemType = "person"
				reasonObjectTypeMC = new PersonViewMC()
				reasonObjectTypeMC.populateObject(reasonListGroupMC.personCB.selectedItem)
				reasonListGroupMC.storyCB.selectedIndex = -1
				reasonListGroupMC.photoTL.selectedIndex = -1
			} else if (event.target.name == "storyCB") {
				serverComm.rsDocument.pirElement.selectedListItem.listItemType = "story"
				reasonObjectTypeMC = new StoryViewMC()
				reasonObjectTypeMC.populateObject(reasonListGroupMC.storyCB.selectedItem)
				reasonListGroupMC.personCB.selectedIndex = -1
				reasonListGroupMC.photoTL.selectedIndex = -1
			} else if (event.target.name == "photoTL") {
			    serverComm.rsDocument.pirElement.selectedListItem.listItemType = "photo"
				reasonObjectTypeMC = new PhotoViewMC()
				reasonObjectTypeMC.populateDP(new DataProvider(reasonListGroupMC.photoTL.selectedItems))
				reasonListGroupMC.personCB.selectedIndex = -1
				reasonListGroupMC.storyCB.selectedIndex = -1
			}
			serverComm.rsDocument.pirElement.selectedListItem.listItemId = event.target.selectedItem.id
			serverComm.toServer(null)
		}
		private function reasonAlphaDone(event:TweenEvent):void {
			removeChild(anExtraObjectMC)
			reasonObjectTypeMC.x = 930
			reasonObjectTypeMC.y = 131
			addChildAt(reasonObjectTypeMC,0)
			reasonObjectTypeMC.alphaTween = new Tween(reasonObjectTypeMC, "alpha", Regular.easeIn, 0, 1, 1, true);
		}
		public function navigationBtnsHandler(event:Event):void {
			serverComm.rsDocument = <rsDocument><pirElement></pirElement></rsDocument>
			serverComm.rsDocument.pirElement.screenName = "relational"
			navigationDirection = event.target.name
			if (event.target.name == "backBtn") {
				serverComm.rsDocument.pirElement.request = "back"
				navigationDirection = "back"
			} else if (event.target.name == "forwardBtn") {
				serverComm.rsDocument.pirElement.request = "forward"
				navigationDirection = "forward"
			}
			serverComm.toServer(navMoveFromServer)
		}
		protected function navMoveFromServer():void {
			checkNavigationBtns(serverComm.rsDocument.pirElement.canBackInNavPath,serverComm.rsDocument.pirElement.foundForwardObject)
			if (navigationDirection == "back") {
				anExtraObjectMC = reasonObjectTypeMC
				reasonObjectTypeMC = manyObjectTypeMC
				manyObjectTypeMC = focusElementMC
				if (serverComm.rsDocument.pirElement.focus.objectType=="person") {
					focusElementMC = new PersonViewMC()
					focusElementMC.populateXML(serverComm.rsDocument.pirElement.focus.persons[0].person[0])
				} else if (serverComm.rsDocument.pirElement.focus.objectType == "story") {
					focusElementMC = new StoryViewMC()
					focusElementMC.populateXML(serverComm.rsDocument.pirElement.focus.stories[0].story[0])
				} else if (serverComm.rsDocument.pirElement.focus.objectType == "photo") {
					focusElementMC = new PhotoViewMC()
					focusElementMC.populateXML(serverComm.rsDocument.pirElement.focus.photos[0].photo[0])
				}
				focusElementMC.x = -400
				focusElementMC.y = 131
				addChildAt(focusElementMC,0)
				anExtraObjectMC.xTween = new Tween(anExtraObjectMC, "x", Regular.easeOut, 930, 1470, 2, true);
				reasonObjectTypeMC.xTween = new Tween(reasonObjectTypeMC, "x", Regular.easeOut, 490, 930, 2, true);
				manyObjectTypeMC.xTween = new Tween(manyObjectTypeMC, "x", Regular.easeOut, 70, 490, 2, true);
				focusElementMC.xTween = new Tween(focusElementMC, "x", Regular.easeOut, -400, 70, 2, true);
			} else if (navigationDirection == "forward") {
				anExtraObjectMC = focusElementMC
				focusElementMC = manyObjectTypeMC
				manyObjectTypeMC = reasonObjectTypeMC
				if (serverComm.rsDocument.pirElement.reason.selectedType=="person") {
					reasonObjectTypeMC = new PersonViewMC()
					reasonObjectTypeMC.populateXML(serverComm.rsDocument.pirElement.reason.persons[0].person[0])
				} else if (serverComm.rsDocument.pirElement.reason.selectedType == "story") {
					reasonObjectTypeMC = new StoryViewMC()
					reasonObjectTypeMC.populateXML(serverComm.rsDocument.pirElement.reason.stories[0].story[0])
				} else if (serverComm.rsDocument.pirElement.reason.selectedType == "photo") {
					reasonObjectTypeMC = new PhotoViewMC()
					reasonObjectTypeMC.populateXML(serverComm.rsDocument.pirElement.reason.photos[0].photo[0])
				}
				reasonObjectTypeMC.x = 1470
				reasonObjectTypeMC.y = 131
				addChildAt(reasonObjectTypeMC,0)
				anExtraObjectMC.xTween = new Tween(anExtraObjectMC, "x", Regular.easeOut, 70, -400, 2, true);
				focusElementMC.xTween = new Tween(focusElementMC, "x", Regular.easeOut, 490, 70, 2, true);
				manyObjectTypeMC.xTween = new Tween(manyObjectTypeMC, "x", Regular.easeOut, 930, 490, 2, true);
				reasonObjectTypeMC.xTween = new Tween(reasonObjectTypeMC, "x", Regular.easeOut, 1470, 930, 2, true);
			}
			manyListGroupMC.personCB.dataProvider = new DataProvider(serverComm.rsDocument.pirElement.many.persons[0])
			manyListGroupMC.storyCB.dataProvider = new DataProvider(serverComm.rsDocument.pirElement.many.stories[0])
			manyListGroupMC.photoTL.dataProvider = new DataProvider(serverComm.rsDocument.pirElement.many.photos[0])
			manyListGroupMC.personCB.addItemAt( { label: "Select", data:0 },0 );
			manyListGroupMC.storyCB.addItemAt( { label: "Select", data:0 },0 );
			reasonListGroupMC.personCB.dataProvider = new DataProvider(serverComm.rsDocument.pirElement.reason.persons[0])
			reasonListGroupMC.storyCB.dataProvider = new DataProvider(serverComm.rsDocument.pirElement.reason.stories[0])
			reasonListGroupMC.photoTL.dataProvider = new DataProvider(serverComm.rsDocument.pirElement.reason.photos[0])
			reasonListGroupMC.personCB.addItemAt( { label: "Select", data:0 },0 );
			reasonListGroupMC.storyCB.addItemAt( { label: "Select", data:0 },0 );
			manyListGroupMC.alphaTween = new Tween(manyListGroupMC, "alpha", Regular.easeIn, 1, 0, 1, true);
			reasonListGroupMC.alphaTween = new Tween(reasonListGroupMC, "alpha", Regular.easeIn, 1, 0, 1, true);
			reasonListGroupMC.alphaTween.addEventListener(TweenEvent.MOTION_FINISH,NavMoveDone)
		}
		private function NavMoveDone(event:TweenEvent):void {
			var listIndex = 1
			var objectId = serverComm.rsDocument.pirElement.many.selectedId
			if (serverComm.rsDocument.pirElement.many.selectedType == "person") {
				for each (item in serverComm.rsDocument.pirElement.many.persons[0].person) 
				{ 
					if (item.@id == objectId) {
						break
					}
					listIndex++
				} 
				manyListGroupMC.personCB.selectedIndex = listIndex
			} else if (serverComm.rsDocument.pirElement.many.selectedType == "story") {
				for each (item in serverComm.rsDocument.pirElement.many.stories[0].story) 
				{ 
					if (item.@id == objectId) {
						break
					}
					listIndex++
				} 
				manyListGroupMC.storyCB.selectedIndex = listIndex
			} else if (serverComm.rsDocument.pirElement.many.selectedType == "photo") {
				for each (item in serverComm.rsDocument.pirElement.many.photos[0].photo) 
				{ 
					if (item.@id == objectId) {
						break
					}
					listIndex++
				} 
				manyListGroupMC.photoTL.selectedIndex = listIndex
			}
			listIndex = 1
			objectId = serverComm.rsDocument.pirElement.reason.selectedId
			if (serverComm.rsDocument.pirElement.reason.selectedType == "person") {
				for each (item in serverComm.rsDocument.pirElement.reason.persons[0].person) 
				{ 
					if (item.@id == objectId) {
						break
					}
					listIndex++
				} 
				reasonListGroupMC.personCB.selectedIndex = listIndex
			} else if (serverComm.rsDocument.pirElement.reason.selectedType == "story") {
				for each (item in serverComm.rsDocument.pirElement.reason.stories[0].story) 
				{ 
					if (item.@id == objectId) {
						break
					}
					listIndex++
				} 
				reasonListGroupMC.storyCB.selectedIndex = listIndex
			} else if (serverComm.rsDocument.pirElement.reason.selectedType == "photo") {
				for each (item in serverComm.rsDocument.pirElement.reason.photos[0].photo) 
				{ 
					if (item.@id == objectId) {
						break
					}
					listIndex++
				} 
				reasonListGroupMC.photoTL.selectedIndex = listIndex
			}
			manyListGroupMC.alphaTween = new Tween(manyListGroupMC, "alpha", Regular.easeOut, 0, 1, 1, true);
			reasonListGroupMC.alphaTween = new Tween(reasonListGroupMC, "alpha", Regular.easeOut, 0, 1, 1, true);
		}
		private function checkNavigationBtns(canBackInNavPath:Number,foundForwardObject:Number):void {
			if (canBackInNavPath) {
				backBtn.enabled = true
			} else {
				backBtn.enabled = false
			}
			if (foundForwardObject == 1) {
				forwardBtn.enabled = true
			} else {
				forwardBtn.enabled = false
			}
		}
	}
}