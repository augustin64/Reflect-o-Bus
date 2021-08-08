function sendJSON(data,callback){
    // Creating a XHR object
    let xhr = new XMLHttpRequest();
    let url = "post";

    // open a connection
    xhr.open("POST", url, true);

    // Set the request header i.e. which type of content you are sending
    xhr.setRequestHeader("Content-Type", "application/json");

    // Create a state change callback
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {

            // Print received data from server
            callback(this.responseText);

        }
    };

    // Converting JSON data to string
    var data = JSON.stringify(data);

    // Sending data with the request
    xhr.send(data);
}

var getJSON = function(url, callback, error_handler=function(err){throw err}) {
    fetch(url)
    .then(res => res.json())
    .then((out) => {
        callback(out);
    })
    .catch(err => { error_handler(err) });
}
