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
  var newSchedule = "<div id='"+id+"'><br/>"
  newSchedule += "Identifiant du bus <input value='"+publicCode+"'><br/>"
  newSchedule += "Direction <input value='"+direction+"' class='direction'><br/>"
  newSchedule += "Arrêt <input class='stop' value='"+stop+"'><br/>"
  if (typeof category === "undefined") {
    newSchedule += "Catégorie <select class='category'><option value=''>DEFAULT</option></select></div>"
  } else {
    newSchedule += "Catégorie <select class='category'><option value='"+category+"'>"+category+"</option><option value=''>DEFAULT</option></select></div>"
    refreshCategories(category)
  }
  document.getElementById('schedules').innerHTML = newSchedule + document.getElementById('schedules').innerHTML
  // Adding category to categories list
  // refreshing all categories
  refreshCategories(undefined)
}

var refreshCategories = function (category) {
  if ((!(category in categories)) && (typeof category != 'undefined')) {
    console.log(category,typeof category != 'undefined')
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
  //Not Implemented
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
  if (value == "True") {
    document.getElementById('lines-color').style.display = "none";
  } else {
    document.getElementById('lines-color').style.display = "inline";
  }
}

var categories = []
getConfig()
bgChange()
linescolorChange()