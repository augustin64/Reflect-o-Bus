var onLoad = function () {
    // On remplace les horaires "0min" par "En Vue"
    for (var i of document.getElementsByClassName('time')) {
        if (i.innerHTML == "0min") { i.innerHTML = "En Vue"}
    }
}

onLoad()