
{
	"Time":	"12:29:00",
	"Latitude":	28.432901382446289,
	"Longitude":	77.306632995605469,
	"Altitude":	207.51,
	"Head":	0,
	"Speed":	0.03,
	"HDOP":	0.6,
	"Quality":	2,
	"Number of Satellite":	36,
	"Differential Age":	0,
	"Date":	120326,
	"NTRIP":	0
}

import os
import json
class GNSSData:
    def __init__(self, filepath):
        """
        :param filepath - path to data file
        """
        self.filepath = filepath
        

    def last_data(self):
        if not os.path.exists(self.filepath):
            print("The specified path does not exist")
            return None

        try:
            with open(self.filepath, 'r') as file:
                data=json.load(file)

            return {"latitude": data["Latitude"], "longitude": data["Longitude"], "Head":data["Head"], "Speed":data["Speed"], "Quality":data["Quality"], "Age":data["Differential Age"],"NTRIP":data["NTRIP"]}

        except Exception as e:
            pass
            #print(f"Error reading GPS data: {e}")

        return None

