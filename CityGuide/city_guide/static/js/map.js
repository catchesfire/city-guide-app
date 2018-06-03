//var waypts;
var waypoints = [];
let isStartPoint = false;
let startLocationInput;
startLocation = localStorage.getItem('start-point');
var transport = "DRIVING";

if(!startLocation){
    localStorage.setItem('start-point', "");
    startLocation = "";
} else{
    if($("#start-location-input").length){
        startLocationInput = $("#start-location-input");
        startLocationInput.val(localStorage.getItem('start-point'));
    }
}

if($("#is-start-point").length){
    isStartPoint = $('#is-start-point')[0].checked;
}

var origin = {};
var destination = {};

function init(way, id = "map"){
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
        center: { lat: 41.85, lng: -87.65 }
    });

    directionsDisplay.setMap(map);

    if(isStartPoint && startLocation != "" && startLocation != undefined){
        getAjax();
        function getAjax(){
            $.ajax({
                url: apiUrl = 'https://maps.google.com/maps/api/geocode/json?address=' + startLocation + '&key=AIzaSyCYXIhgWd59IDdrJoO38Tz2hbyoYw0u9TU'
            }).done(function(data){
                if(data.status == "OK"){
                    let address = data.results[0]['formatted_address'];
                    startLocation = address;
                    startLocationInput.val(address);
                    calculateAndDisplayRoute(directionsService, directionsDisplay, data.results[0].geometry.location);
                } else{
                    setTimeout(getAjax, 1000);
                }
            });
        }
    } else{
        calculateAndDisplayRoute(directionsService, directionsDisplay);
    }
}

function calculateAndDisplayRoute(directionsService, directionsDisplay, pos = {}) {
    waypoints = [];

    if($('#transport').length){
        transport = $('#transport').val();
    }

    var i = 1;
    origin = {
        lat: waypts[0].lat,
        lng: waypts[0].lng
    }

    if(isStartPoint){
        i = 0;
        origin = {
            lat: pos.lat,
            lng: pos.lng
        }
    }

    for(i; i < Object.keys(waypts).length - 1; i++){
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
            //var summaryPanel = document.getElementById('directions-panel');
            //summaryPanel.innerHTML = '';
            // For each route, display summary information.
            //console.log(route);
            //var i = 0;
            //$('.route-steps').each(function(){
            //    $(this).html("");
            //})
            //$('.attraction').each(function(){
            //    steps = $(this).find('.route-steps');
            //    var string = "";
            //   for(var j = 0; j < route.legs[i].steps.length; j++){
            //        string += route.legs[i].steps[j].instructions + "<br>";
            //    }
            //    steps.html(string);

            //    if(i < route.legs.length)
            //        i++;
            //});
            //if(isStartPoint){
                //d = document.createElement('div');
               // $(d).attr('id', "block-0");
               // d.innerHTML += route.legs[0].start_address + ' to ';
              //  d.innerHTML += route.legs[0].end_address + '<br>';
               // d.innerHTML += route.legs[0].distance.text + '<br><br>';
             //   $('#sortable').prepend(d);
            //}
            //$('.attraction').not
            //for (var i = 0; i < route.legs.length; i++) {
                //var routeSegment = i + 1;
                   // summaryPanel.innerHTML += '<b>Route Segment: ' + routeSegment +
                    //    '</b><br>';
                  //  summaryPanel.innerHTML += route.legs[i].start_address + ' to ';
                //    summaryPanel.innerHTML += route.legs[i].end_address + '<br>';
              //      summaryPanel.innerHTML += route.legs[i].distance.text + '<br><br>';
            //}
        } else {
            window.alert('Directions request failed due to ' + status);
        }
    });
}