var getSchedules = function (fontSize=1) {
    getJSON("/get?content=horaires", function(data){
        data = data["data"];
        shape = data["config"]["shape"];
        // Variables initialisation dependingnon the request content
        var numberOfCategories = Object.keys( data["schedule"] ).length;
        var numberOfSchedules = 0;
        for (var category of Object.keys( data["schedule"] ) ) {
            numberOfSchedules += data["schedule"][category].length;
        }
        if (numberOfSchedules == 0) {
            // If no schedules are available, we set te text to this sentence
            document.body.innerHTML = "<center>Aucun horaire en temps réel n'est disponible,<br/>Configurez cela à l'URL suivante : <a href=\"http://"+data["config"]["localip"]+":5000\">http://"+data["config"]["localip"]+":5000</a></center>";
        } else {
            section = "<section style='padding-left:5%;'>"
            for (var category of Object.keys( data["schedule"] ) ) {
                // We set the beginning of the section
                section += "<div class='schedule' style='width:"+90/numberOfCategories+"%;'>"
                if ( ! data["config"]["hide_category"]){
                    // If the variable hide_category is set to 
                    // true, we don't display the title
                    section += "<h3>"+category+"</h3>"
                }
                if ( data["schedule"][category].length > 0 ) {
                    for (var schedule of data["schedule"][category]) {
                        section += "<div id='"+shape+"' style='background-color: "
                        if (data['config']['pass_colors']) {
                            // We set the squircle color to
                            // the parameters
                            section += schedule["color"]
                        } else {
                            section += data['config']['lines_color']
                        }
                        section += ";'>"
                        section += "<p>"+schedule["PublicCode"]+"</p></div>";
                        section += "<span style='font-size:"+fontSize+"rem;' class='time";
                        if ( schedule["isRealTime"] ) { 
                            section += " realtime" 
                        }
                        if (schedule['hour'] == 0) {
                            section += "'>En Vue</span>"
                        } else {
                            section += "'>"+schedule["hour"]+"min</span>"
                        }
                    }
                } else {
                    section += "Il n'y a pas d'horaires disponibles pour cette catégorie"
                }
                section += "</div>"
            }
            section += "</select>"
            document.body.innerHTML = section
        }
    }, error_handler=function(err){
        document.body.innerHTML=err;
        console.log(err);
        setTimeout(() => {document.location=document.location},1000)
    });
    // On remplace les horaires "0min" par "En Vue"
    for (var i of document.getElementsByClassName('time')) {
        if (i.innerHTML == "0min") { i.innerHTML = "En Vue"}
    }
}

var loadLook = function() {
    getJSON("/get?content=look", function(data){
        data = data["data"];
        
        if (typeof data["background_url"] != "undefined") {
            document.body.style.background = "url(/static/walls/"+data["background_url"]+")";
        } else {
            document.body.style.background = "url(/not_an_image.png)"
        }
        document.body.style.backgroundColor = data["background_color"];
        
        for (element of document.getElementsByClassName("time")) {
            element.style.fontSize = data["font_size"]+"rem";
        }
        if (window.cpt == 3) {
            getSchedules(fontSize=data["font_size"]);
            window.cpt = 0;
        } else {
            window.cpt += 1;
        }
        setTimeout(() => {  loadLook("loadLook"); }, data["refresh_time"]/3 );
    });
}

var onLoad = function() {
    getSchedules();
    loadLook()
}

window.cpt = 0;
onLoad()


// N'affiche pas Internal Server Error si c'est le cas