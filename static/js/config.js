var getConfig = function() {
  getJSON('get?content=config',
  function(data) {
    for (var i in data) {
      if ( i == "DEFAULT" ) {
        for (var j in data[i]) {
          document.getElementById(j).value = data[i][j]
        }
      } else {
        if ( i == "ADVANCED" ) {
          for (var j in data[i]) {
            document.getElementById(j).value = data[i][j]
          }
        } else {
          if (true) {
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
    }
  });
}

var addSchedule = function (id,publicCode,direction,stop,category) {
  // Adding schedule to html
  var newSchedule = "<div id='"+id+"'><br/>"
  newSchedule += "Identifiant du bus <input value='"+publicCode+"'><br/>"
  newSchedule += "Direction <input value='"+direction+"'><br/>"
  newSchedule += "Arrêt <input class='stop' value='"+stop+"'><br/>"
  newSchedule += "Catégorie <select><option value='category'>"+category+"</option><option value=''>DEFAULT</option></select></div>"
  document.getElementById('schedules').innerHTML = newSchedule + document.getElementById('schedules').innerHTML
  // Adding category to categories list
  // refreshing all categories
}

var refreshCategories = function () {
  //Not Implemented
}

