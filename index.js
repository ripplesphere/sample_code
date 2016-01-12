$(document).ready(function() {

   $("#displayed_name_input").on('keypress', function (event) {
         if (event.which === 13) {
            submitNewPerson();
         }
   });

   $("#event_title_input").on('keypress', function (event) {
         if (event.which === 13) {
            submitNewEvent();
         }
   });

});

var CLIENT_ID = '';
var SCOPES = ['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/plus.login',
              'https://www.googleapis.com/auth/plus.me'];
var unique_count = 1;
var my_id;

function checkAuth() {
  gapi.auth.authorize(
    {
      'client_id': CLIENT_ID,
      'scope': SCOPES.join(' '),
      'immediate': true
    }, handleAuthResult);
}

function handleAuthResult(authResult) {
  var authorizeDiv = document.getElementById('authorize-div');
  if (authResult && !authResult.error) {
    authorizeDiv.style.display = 'none';
    var apisToLoad = 2;
    gapi.client.load('drive', 'v3');
    gapi.client.load('plus', 'v1', getMyId);
  } else {
    authorizeDiv.style.display = 'inline';
  }
}

function handleAuthClick(event) {
  gapi.auth.authorize(
    {client_id: CLIENT_ID, scope: SCOPES, immediate: false},
    handleAuthResult);
  return false;
}

// https://accounts.google.com/logout

function getMyId() {
   var request = gapi.client.plus.people.get({ 'userId' : 'me' });
   request.execute(function(resp) {
      my_id = resp.id;
      $.ajax({
         type: "POST",
         url: "/operation",
         dataType: 'json',
         data: { 'user_id': my_id, 'operation': 'store_me', 'person_id': resp.id, 'display_name': resp.displayName, 
                  'image_url': resp.image.url 
         }
      }).always(function(data) {
         getAllEvents();
         getAllPhotos();
         getAllPeople();
      });
   });
}

function getAllPeople() {
   var request = gapi.client.plus.people.list({ 'userId' : 'me', 'collection' : 'visible' });
   request.execute(function(resp) {
      var people_list = JSON.stringify(resp.items);
      console.log("people list: " + people_list);
      $.ajax({
         type: "POST",
         url: "/operation",
         dataType: 'json',
         data: { 'user_id': my_id, 'operation': 'get_all_people', 'people_list': people_list
         }
      }).always(function(data) {
         console.log("data: " + data);
         for (var i = 0; i < data.length; i++) {
            console.log("people display_name: " + data[i].display_name);
            personEleStr = '<li><a href="/person_display/' + data[i].person_id + '"><img src="' + 
                          data[i].image_url + '"/><p>' + data[i].display_name + '</p></a></li>';
            $("#available_people").append(personEleStr);
         }
      });
   });
}

function getAllPhotos() {
   var query = "'root' in parents and name = 'Chronicler' and " +
      "mimeType = 'application/vnd.google-apps.folder' and not trashed";
   gapi.client.drive.files.list({'q': query}).execute(function(resp) {
      if (resp.files.length == 1) {
         appFolderId = resp.files[0].id;
         var imgQuery = "'" + appFolderId + "' in parents and mimeType contains 'image/' and not trashed";
         gapi.client.drive.files.list({'q': imgQuery, 'orderBy': 'createdTime'}).execute(function(resp) {
            for (var i = 0; i < resp.files.length; i++) {
               gapi.client.drive.files.get({'fileId': resp.files[i].id, 'fields': "id, name, thumbnailLink" }).execute(function(fileResp) {
                  var drive_id = fileResp.id;
                  var imgTitle = fileResp.name;
                  $.ajax({
                     type: "POST",
                     url: "/operation",
                     dataType: 'json',
                     data: { 'user_id': my_id, 'operation': 'photo_verify', 'title': imgTitle, 'drive_id': drive_id, 
                              'thumbnailLink': fileResp.thumbnailLink
                        }
                  }).always(function(data) {
                     var imgEleString = '<a href="/photo_display/' + data + '"><img class="img-thumbnail" src="' +  
                                          fileResp.thumbnailLink + '"/></a>';
                     $("#all_photos").append(imgEleString);
                  });


               });
            }
         });
      } else {
         gapi.client.drive.files.insert({'title': 'Chronicler', 'parents': 'root', 
                                          'mimeType': 'application/vnd.google-apps.folder'}).execute(function(resp1) {
               appFolderId = resp1.id;
         });
      }
   });
}

function getAllEvents() {
   $.ajax({
      type: "POST",
      url: "/operation",
      dataType: 'json',
      data: { 'user_id': my_id, 'operation': 'get_all_events'
      }
   }).always(function(data) {
      for (var i = 0; i < data.length; i++) {
         eventEleStr = '<a href="/event_display/' + data[i].event_id + '"><h3>' + data[i].event_title + '</h3></a>';
         $("#all_events").append(eventEleStr);
      }
   });
}

function submitNewPerson() {
   var name_value =  $.trim( $('#displayed_name_input').val() )
   if (name_value != "") {
      $.ajax({
         type: "POST",
         url: "/operation",
         dataType: 'json',
         data: { 'user_id': my_id, 'operation': 'new_person', 'display_name': name_value
            }
      }).always(function(data) {
         var person_id = data;
         $("#new_person_form > #person_id").val(person_id);
         $("#new_person_form > #user_id").val(my_id);
         $("#new_person_form").submit();
      });
   }
}

function submitNewEvent() {
   var title_value =  $.trim( $('#event_title_input').val() )
   if (title_value != "") {
      $.ajax({
         type: "POST",
         url: "/operation",
         dataType: 'json',
         data: { 'user_id': my_id, 'operation': 'new_event', 'title': title_value
            }
      }).always(function(data) {
         var event_id = data;
         $("#new_event_form > #event_id").val(event_id);
         $("#new_event_form > #user_id").val(my_id);
         $("#new_event_form").submit();
      });
   }
}

function fileSelected() { 
   var fileInput = document.querySelector("#upload_file");
   var files = fileInput.files;
   var fl=files.length;
   var i=0;

   const boundary = '-------314159265358979323846';
   const delimiter = "\r\n--" + boundary + "\r\n";
   const close_delim = "\r\n--" + boundary + "--";

   while ( i < fl) {
        var fileData = files[i];
        var reader = new FileReader();
        reader.readAsBinaryString(fileData);
        reader.onload = function(e) {
          var contentType = fileData.type || 'application/octet-stream';
          var metadata = { 'name': fileData.name, 'mimeType': contentType, 'parents': [ appFolderId ] };
          var base64Data = btoa(reader.result);
          var multipartRequestBody = delimiter + 'Content-Type: application/json\r\n\r\n' +
              JSON.stringify(metadata) + delimiter + 'Content-Type: ' + contentType + '\r\n' + 
              'Content-Transfer-Encoding: base64\r\n' + '\r\n' + base64Data + close_delim;

           var xhr = new XMLHttpRequest();

           xhr.open('POST', 'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart', true);

           xhr.setRequestHeader('Content-Type', 'multipart/mixed; boundary="' + boundary + '"');
           xhr.setRequestHeader('authorization', 'Bearer ' + gapi.auth.getToken().access_token);

           xhr.upload.addEventListener("progress", function(e) {
                var percentage = parseFloat(e.loaded / e.total * 100).toFixed(2);
                $('.progress-bar').css({ 'width': percentage + '%' });
                $('.progressText').html(Math.round(percentage + "%"));
           }, false);

           xhr.onreadystatechange = function(e) {
             if (xhr.readyState == 4) {
               var jsonResponse = JSON.parse(xhr.responseText);
               fileUploaded(jsonResponse);
             }
           };

           xhr.send(multipartRequestBody);


          $("#upload_file").hide();
          $("#file_progress_bar").show();
       }
       i++;
     }    
}

function fileUploaded(response) {
   $.ajax({
      type: "POST",
      url: "/operation",
      dataType: 'json',
      data: { 'user_id': my_id, 'operation': 'new_photo', 'title': response.name, 'photo_id': response.id, 
               'thumbnailLink': response.thumbnailLink
         }
   }).always(function(data) {
      var photo_id = data;
      $("#new_photo_form > #photo_id").val(photo_id);
      $("#new_photo_form > #user_id").val(my_id);
      $("#new_photo_form").submit();
   });
}

