import csv
import json
import slumber

api = slumber.API('https://hrvawiki.org/api/')
username = ''
api_key = ''
counter = 0

with open('portsmouth-path-of-history.csv', 'rb') as f:
    reader = csv.DictReader(f)
    for row in reader:
        counter += 1
        try:
            print 'Adding page ' + str(counter) + ': ' + row['Description']
        
            print api.page.post(
                {
                    'name': row['Description'], 
                    'content': '<p>' + row['Location'] + '</p><p class="walking-tour-info">Portsmouth Walking Tour - <span class="walking-tour-id">' + row['Walking Tour Number'] + '</span></p>'
                }, 
                username=username, api_key=api_key
            )
        
            tags = ['/api/tag/portsmouth', '/api/tag/walkingtour']
            if(row['Path of History'] == 'Y'):
                tags.append('/api/tag/pathofhistory')
            print api.page_tags.post(
                {'page': '/api/page/' + row['Description'], 'tags': tags}, username=username, api_key=api_key
            )
        
            print api.map.post(
                {
                    "page": "/api/page/" + row['Description'],
                    "geom": {
                        "geometries": [{
                            "coordinates": [float(row['Longitude']), float(row['Latitude'])],
                            "type": "Point"
                        }],
                        "type": "GeometryCollection"
                    }
                },
                username=username, api_key=api_key
            )
        except:
            print 'Fail'
