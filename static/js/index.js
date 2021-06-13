shutdown = function () {
    if ( confirm("Souhaitez-vous éteindre l'écran ?") ) {
        sendJSON({
            "action":"shutdown",
            "data":{},
        }, 
        function (data) {
            null
        })
    }
}