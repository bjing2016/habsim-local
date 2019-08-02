import random
import math
class RandomColorGenerator:
    '''
    Generates random web-compatible colors.
    Can be accessed like a list.
    '''
    def __init__(self):
        pass
        
    def __getitem__(self, key):
        red, green, blue = random.choices(["00", "33", "66", "99", "CC"], k=3)
        return '#' + red + green + blue

    def __len__(self):
        return 10 ** 10

def get_html_marker_string(lat, lon, label, title):
    '''
    Internal method. Do not use.
    '''
    return '''var marker = new google.maps.Marker({
            position: {lat: ''' + str(lat)+''', lng: ''' + str(lon) + '''},
            label: " ''' + label + ''' ",
            title:" ''' + title + ''' "
        });
        // To add the marker to the map, call setMap();
        marker.setMap(map);
    '''

def get_html_path_string(path_cache, color, counter, weight=2):
    '''
    Internal method. Do not use.
    '''
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
          strokeWeight: """ + str(weight) + """
        });

        flightPath"""+str(counter) + """.setMap(map);"""
    return string

default_colors = ["#000000", "#FF0000", "#008000", "#800000", "#808000"]
class WebPlot:
    '''
    A WebPlot writes an HTML file where trajectories can be viewed in an OpenStreetMap interface.
    '''
    def __init__(self):
        self.pathstring = ""
        self.counter = 0

    def add(self, trajectories, colors = default_colors, weight=2):
        '''
        Adds a list of trajectories. If list is longer than 5, colors must be specified.
        Whenever this method is called, the list of colors is used from the beginning.
        Therefore passing in segments seperately is not the same as passing in a list.
        '''
        if len(trajectories) > len(colors):
            raise Exception("Longest trajectory longer than number of colors.")
        
        for i in range(len(trajectories)):
            self.pathstring += get_html_path_string(trajectories[i], colors[i], self.counter, weight)
            self.counter += 1

    def marker(self, lat, lon, label="", title=""):
        '''
        Adds a marker with a visible label and a title shown upon mouseover.
        '''
        self.pathstring += get_html_marker_string(lat, lon, label, title)

    def origin(self, lat, lon, zoom=7):
        '''
        Sets the origin of the plot. Must be called.
        '''
        self.slat = lat
        self.slon = lon
        self.zoom = zoom
    
    def save(self, name):
        '''
        Writes file to disk.
        '''
        f = open(name, "w")
        f.write(part1 + str(self.slat) + "," + str(self.slon) + "),zoom:" + str(self.zoom))
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
                
part2 = ''' ,
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