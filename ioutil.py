def get_html_path_string(path_cache, color, counter):
    string =  "var flightPlanCoordinates" + str(counter) + " = [ \n"
    for pair in path_cache:
        string = string + "{lat: " + str(pair[1]) + ", lng: " + str(pair[2]) + "},\n"
    string = string + """
        ];
        var flightPath""" + str(counter) + """ = new google.maps.Polyline({
          path: flightPlanCoordinates"""+str(counter)+""",
          geodesic: true,
          strokeColor: '""" + color + """',
          strokeOpacity: 1.0,
          strokeWeight: 2
        });

        flightPath"""+str(counter) + """.setMap(map);"""
    
    counter = counter + 1
    return string

default_colors = ["#000000", "#FF0000", "#008000", "#800000", "#808000"]

class webplot:
    def __init__(self):
        self.pathstring = ""
        self.counter = 0

    def add(self, trajectories, colors = default_colors):
        if len(trajectories) > len(colors):
            raise Exception("Please specify colors")
        
        for i in range(len(trajectories)):
            self.pathstring += get_html_path_string(trajectories[i], colors[i], self.counter)
            self.counter += 1

    def origin(self, lat, lon):
        self.slat = lat
        self.slon = lon
    
    def save(self, name):
        f = open(name, "w")
        f.write(part1 + str(self.slat) + "," + str(self.slon))
        f.write(part2)
        f.write(self.pathstring)
        f.write(part3short)
        f.write(part4 + part5)
        f.close()

#########

part1 = '''

<!DOCTYPE html>
<html>
    <head>
        <meta name="viewport" content="initial-scale=1.0, user-scalable=yes" />
         <style type="text/css">
 		html { height: 100% }
	    body { height: 100%; margin: 0; padding: 0 }            
		#map{
                height: 100%;
                width: 100%;
                margin: 0;
                padding: 0;
            }
        </style> 
    </head>
    <body>
        <div id="map" style="float: left;"></div>       
        <!-- bring in the google maps library -->
        <script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?sensor=false"></script>
        <script type="text/javascript">
            //Google maps API initialisation
            var element = document.getElementById("map");
            var map = new google.maps.Map(element, {
                center: new google.maps.LatLng('''
                
part2 = ''' ),
                zoom: 9,
                mapTypeId: "OSM",      
            });
            google.maps.event.addListener(map, 'click', function (event) {
              displayCoordinates(event.latLng);               
            });
 
            //Define OSM map type pointing at the OpenStreetMap tile server
            map.mapTypes.set("OSM", new google.maps.ImageMapType({
                getTileUrl: function(coord, zoom) {
                    // "Wrap" x (longitude) at 180th meridian properly
                    // NB: Don't touch coord.x: because coord param is by reference, and changing its x property breaks something in Google's lib
                  var tilesPerGlobe = 1 << zoom;
                    var x = coord.x % tilesPerGlobe;
                    if (x < 0) {
                        x = tilesPerGlobe+x;
                    }
                    // Wrap y (latitude) in a like manner if you want to enable vertical infinite scrolling

                    return "https://tile.openstreetmap.org/" + zoom + "/" + x + "/" + coord.y + ".png";
                },
                tileSize: new google.maps.Size(256, 256),
                name: "OpenStreetMap",
                maxZoom: 18
            }));
''' 

part3short = '''
        </script>
    <div id="map_canvas" style="width:80%; height:100%"></div>
    <div id="info" style="padding-left:2ch; padding-right: 2ch">

      <div>
   
'''

part4 = '''

      </div>
    </div>
    '''
part5 = '''
</body>
</html>
'''