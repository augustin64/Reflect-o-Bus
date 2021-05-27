var getConfig = function() {
  getJSON('get?content=config',
  function(data) {
    for (var i in data) {
      if ( i == "DEFAULT" || i == "ADVANCED" ) {
        for (var j in data[i]) {
          document.getElementById(j).value = data[i][j]
        }
      } else {
        if (i.includes("schedule")) {
          addSchedule(
            i.split("/")[1],
            data[i]['publiccode'],
            data[i]['direction'],
            data[i]['stop'],
            data[i]['category']
          )
        } else {      
          console.log(i);
          console.log(data[i])
        }
      }
    }
  });
}

var addSchedule = function (id,publicCode,direction,stop,category) {
  // Adding schedule to html
  var newSchedule = "<br/><div id='"+id+"'>"
  newSchedule += "Identifiant du bus <input class='publiccode' value='"+publicCode+"'><br/>"
  newSchedule += "Direction <input value='"+direction+"' class='direction'><br/>"
  newSchedule += "Arrêt <input class='stop' value='"+stop+"'><br/>"
  // Setting current category as 1st of the list
  if (typeof category === "undefined") {
    newSchedule += "Catégorie <select class='category'><option value=''>DEFAULT</option></select>"
  } else {
    newSchedule += "Catégorie <select class='category'><option value='"+category+"'>"+category+"</option><option value=''>DEFAULT</option></select>"
    refreshCategories(category);
  }
  newSchedule += "<button onclick=\"deleteSchedule('"+id+"')\">Supprimer</button></div>"

  document.getElementById('schedules').innerHTML = newSchedule + document.getElementById('schedules').innerHTML;
  // Adding category to categories list &
  // refreshing all categories
  refreshCategories(undefined);
}

var deleteSchedule = function (id) {
  var element = document.getElementById(id);
  element.remove()
}

var refreshCategories = function (category) {
  if ((!(category in categories)) && (typeof category != 'undefined')) {
    categories.push(category);
  }
  var divs = document.getElementsByClassName('category');
  for (var i of divs) {
    for (var j of categories) {
      if (! i.innerHTML.includes(j)) {
        i.innerHTML += "<option value='"+j+"'>"+j+"</option>"
      }
    }
  }

}

var addCategory = function () {
  var category = prompt("Quelle catégorie souhaitez vous créer ?", "");
  refreshCategories(category)
}

var userAddSchedule = function () {
  var id = prompt("Quel identifiant souhaitez vous donner à cet horaire ?")
  id = id.replace(' ','_')
  addSchedule(
    id,
    "",
    "",
    "",
    undefined
  )
}

var bgChange = function () {
  var e = document.getElementById("background_type");
  var bg_type = (e.value);
  if (bg_type == "color") {
    document.getElementById("background-color-span").style.display = "inline";
    document.getElementById("background-image-span").style.display = "none";
  } else {
    document.getElementById("background-color-span").style.display = "none";
    document.getElementById("background-image-span").style.display = "inline";
  }
}
var linescolorChange = function () {
  var e = document.getElementById('pass_colors');
  var value = e.options[e.selectedIndex].value;
  if (value == "False") {
    document.getElementById('lines-color').style.display = "inline";
  } else {
    document.getElementById('lines-color').style.display = "none";
  }
}

var sendConfig = function () {
  var data = {}
  data['DEFAULT'] = {}
  data['ADVANCED'] = {}
  schedules = []
  for (var i of document.getElementById('main-config').getElementsByTagName('input')) {
    data['DEFAULT'][i.id] = i.value
  }
  for (var i of document.getElementById('ADVANCED').getElementsByTagName('input')) {
    data['ADVANCED'][i.id] = i.value
  }
  for (var i of document.getElementById('ADVANCED').getElementsByTagName('select')) {
    data['ADVANCED'][i.id] = i.options[i.selectedIndex].value;
  }
  for (var i of document.getElementById('schedules').getElementsByTagName('div')) {
    schedules.push(i.id)
    data['schedule/'+i.id] = {}
    data['schedule/'+i.id]["publiccode"] = i.getElementsByClassName('publiccode')[0].value;
    data['schedule/'+i.id]["direction"] = i.getElementsByClassName('direction')[0].value;
    data['schedule/'+i.id]["stop"] = i.getElementsByClassName('stop')[0].value;
    var e = i.getElementsByClassName('category')[0];
    if ( ! e.options[e.selectedIndex].value == "") {
      console.log(e.options[e.selectedIndex].value)
      data['schedule/'+i.id]["category"] = e.options[e.selectedIndex].value;
    }
  }
  data['DEFAULT']['schedules'] = schedules.join(' ')
  content = {
    "data":data,
    "action":"setConfig"
  }
  sendJSON(content,function (data) {
    console.log(data);
  })
  alert('✔️ Configuration mise à jour')
}

getWifi = function () {
  SSID = prompt("Quel est l'identifiant du réseau sans fil ?","")
  pass = prompt("Quel est le mot de passe du réseau sans fil ?","")
  sendJSON({
    "action":"set_WLAN",
    "data":{
      "SSID":SSID,
      "password":pass,
    }
  }, function (data) {
      alert(data);
  });
}

var categories = []
getConfig()
bgChange()
linescolorChange()