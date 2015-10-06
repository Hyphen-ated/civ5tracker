function load_piece(id) {
    var req = new XMLHttpRequest();
    var result = ";"
    req.onreadystatechange = function() {
        if (req.readyState != 4) return; // Not there yet
        var errorelem = document.getElementById("error");
        if (req.status != 200) {
            errorelem.innerHTML = "error, can't load data (tracker server shut down?)";
            return;
        } else {
            result = req.responseText;
            errorelem.innerHTML = "";
        }
        var elem = document.getElementById(id);
        elem.innerHTML = result;
    }
    req.open("GET", "http://localhost:8085/" + id + ".txt", true);
    req.send();

}

function reload() {
    load_piece("pol")
    load_piece("rel")
    load_piece("wonders")


}
setInterval(reload, 3000);