const API_SERVER = window.location.origin;
var searchResultElem;

function callAPI(path, method, data, callback) {
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener("readystatechange", function () {
        if (this.readyState === 4) {
            callback(JSON.parse(this.responseText));
        }
    });

    xhr.open(method, path);
    xhr.setRequestHeader("content-type", "application/json");
    xhr.setRequestHeader("cache-control", "no-cache");
    console.log(data);
    xhr.send(data);

}


var lastQuery = "";
function customChangeEvent(bar) {
    var newQuery = bar.value;
    if (newQuery !== lastQuery) {
        console.log("CHANGE");
        lastQuery = newQuery;
        sendQuery(newQuery);
    }
}

function sendQuery(query){

    searchResultElem.style.display = "none";

    var data = {
        "query" : query
    };

    getInvites(function (result) {
        console.log(result);
        searchResultElem.style.display = "block";

        var container = document.getElementById('invite-records');
        container.innerHTML = "";


        if (result.data.length > 0) {
            result.data.forEach(function (item) {
                // console.log('contact_info: ' + item.subject);

                var cardInvite = document.createElement('div');
                cardInvite.id = "card-invite";
                cardInvite.style.backgroundColor = 'aquamarine'

                cardInvite.style.backgroundColor = '#00aee'

                var content = document.createElement('p');
                content.id = 'card-invite-detail'
                var distance = parseFloat(item.euclidean);
                distance = distance.toFixed(2);
                content.textContent = item.subject + " - distance " + distance;

                var toolTip = document.createElement('span');
                toolTip.id = "tooltiptext";
                toolTip.innerHTML = item.content;

                
                // cardInvite.onclick = function () {
                //     // window.location.href = API_SERVER + "/invite/" + item.id;
                // };

                cardInvite.appendChild(content);
                cardInvite.appendChild(toolTip);
                container.appendChild(cardInvite);
            });
        } else {
            var noP = document.createElement('p');
            noP.textContent = 'No Data Found !!'
            container.appendChild(noP);
        }
    }, JSON.stringify(data));
}

function pageReady(request, response) {

    var searchBar = document.getElementById("search-email");
    searchResultElem = document.getElementById("invite-records");
    setInterval(() => {
        customChangeEvent(searchBar);
    }, 100);
}

function getInvites(callback, data) {
    callAPI(API_SERVER + "/get_relevant", "POST", data, function (response) {
        callback(response);
    });
}