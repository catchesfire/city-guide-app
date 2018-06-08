//var waypts;
var waypoints = [];
let isStartPoint = false;
let startLocationInput;
startLocation = localStorage.getItem('start-point');
var transport = localStorage.getItem('transport');

if (!startLocation) {
    localStorage.setItem('start-point', "");
    startLocation = "";
} else {
    if ($("#start-location-input").length) {
        startLocationInput = $("#start-location-input");
        startLocationInput.val(localStorage.getItem('start-point'));
    }
}
if(!transport){
    localStorage.setItem('transport', 'DRIVING');
    transport = "DRIVING";
} else{
    if($("#transport").length){
        $("#transport").val(localStorage.getItem('transport'));
        transport = localStorage.getItem('transport');
    }
}

if ($("#is-start-point").length) {
    isStartPoint = $('#is-start-point')[0].checked;
}

var origin = {};
var destination = {};

function init(way, id = "map") {
    mapId = id;
    startLocationInput = $('#start-location-input');

    origin = {
        lat: way[0].lat,
        lng: way[0].lng
    };

    var wayptsSize = Object.keys(way).length;

    destination = {
        lat: way[wayptsSize - 1].lat,
        lng: way[wayptsSize - 1].lng
    };

    initMap();
}

function initMap() {
    var directionsService = new google.maps.DirectionsService;
    var directionsDisplay = new google.maps.DirectionsRenderer;
    var map = new google.maps.Map(document.getElementById(mapId), {
        zoom: 6,
        center: { lat: 53.1182885, lng: 23.1497195 }
    });

    directionsDisplay.setMap(map);

    if (isStartPoint && startLocation != "" && startLocation != undefined) {
        getAjax();
        function getAjax() {
            $.ajax({
                url: apiUrl = 'https://maps.google.com/maps/api/geocode/json?address=' + startLocation + '&key=AIzaSyCYXIhgWd59IDdrJoO38Tz2hbyoYw0u9TU'
            }).done(function (data) {
                if (data.status == "OK") {
                    let address = data.results[0]['formatted_address'];
                    startLocation = address;
                    startLocationInput.val(address);
                    calculateAndDisplayRoute(directionsService, directionsDisplay, data.results[0].geometry.location, mapId);
                    //$('#map-9').show();
                } else {
                    setTimeout(getAjax, 1000);
                }
            });
        }
    } else {
        calculateAndDisplayRoute(directionsService, directionsDisplay, {}, mapId);
        //$('#' + mapId).show();
    }
}

function minToHours(time){
    let days = Math.floor(time / 1440);
    
    if (days > 0){
        time -= 1440;
    }

    hours = Math.floor(time / 60)
    time -= 60 * hours
    minutes = time 
    
    let daysStr = (days == 1) ? days + " dzień" :  (days != 0) ? days + " dni" : "";
    let hoursStr = (hours > 0) ? hours + " godz." : "";
    let minutesStr = (minutes > 0) ? minutes + " min" : ""; 

    return daysStr + " " + hoursStr + " " + minutesStr;
} 

function calculateAndDisplayRoute(directionsService, directionsDisplay, pos = {}, map) {
    waypoints = [];

    if ($('#transport').length) {
        transport = $('#transport').val();
    }

    var i = 1;
    origin = {
        lat: waypts[0].lat,
        lng: waypts[0].lng
    }

    if (isStartPoint) {
        i = 0;
        origin = {
            lat: pos.lat,
            lng: pos.lng
        }
    }

    for (i; i < Object.keys(waypts).length - 1; i++) {
        waypoints.push({
            location: new google.maps.LatLng({ lat: waypts[i].lat, lng: waypts[i].lng }),
            stopover: true
        });
    }

    directionsService.route({
        origin: new google.maps.LatLng(origin),
        destination: new google.maps.LatLng(destination),
        waypoints: waypoints,
        optimizeWaypoints: dirty ? false : true,
        travelMode: transport
    }, function (response, status) {
        if (status === 'OK') {
            directionsDisplay.setDirections(response);
            var route = response.routes[0];

            let travelTime = 0;
            route.legs.forEach(edge => {
                travelTime += parseInt(edge.duration.text.split(' '[0]));
            });
            
            if($('#total-time').length){
                let time = parseInt(document.getElementById('total-time').innerHTML)
                time += travelTime;
                document.getElementById('total-time').innerHTML = minToHours(time);
                $('#total-time').css('display', 'inline');
            }
            $('#spinner-' + map).fadeOut("slow", function(){
              $('#' + map).animate({
                opacity: "1" 
              }, 500);
            });
        } else {
            window.alert('Directions request failed due to ' + status);
        }
    });
}