import os

import shapefile as sf
from plot_catchment import plot_catchment

import pyromb

DIR = os.path.dirname(__file__)
REACH_PATH = os.path.join(DIR, '../data', 'reaches.shp')
BASIN_PATH = os.path.join(DIR, '../data', 'basins.shp')
CENTROID_PATH = os.path.join(DIR, '../data', 'centroids.shp')
CONFUL_PATH = os.path.join(DIR, '../data', 'confluences.shp')

class SFVectorLayer(sf.Reader, pyromb.VectorLayer):
    """Wrap the shapefile.Reader() with the necessary interface
    to work with the builder. 
    """
    def __init__(self, path) -> None:
        super().__init__(path)

    def geometry(self, i) -> list:
        return self.shape(i).points

    def record(self, i) -> dict:
        return super().record(i)

    def __len__(self) -> int:
        return super().__len__()

def main():
    ### Config ###
    plot = False # Set True of you want the catchment to be plotted
    model = pyromb.RORB() # Select your hydrology model, either pyromb.RORB() or pyromb.WBNM()

    ### Build Catchment Objects ###
    # Vector layers
    reach_vector = SFVectorLayer(REACH_PATH)
    basin_vector = SFVectorLayer(BASIN_PATH)
    centroid_vector = SFVectorLayer(CENTROID_PATH)
    confluence_vector = SFVectorLayer(CONFUL_PATH)
    # Create the builder.
    builder = pyromb.Builder()
    # Build each element as per the vector layer.
    tr = builder.reach(reach_vector)
    tc = builder.confluence(confluence_vector)
    tb = builder.basin(centroid_vector, basin_vector)

    ### Create the catchment ###
    catchment = pyromb.Catchment(tc, tb, tr)
    connected = catchment.connect()
    # Create the traveller and pass the catchment.
    traveller = pyromb.Traveller(catchment)

    ### Write ###
    # Control vector to file with a call to the Traveller's getVector method
    with open(os.path.join(DIR, '../vector.catg' if isinstance(model, pyromb.RORB) else '../runfile.wbn'), 'w') as f:
        f.write(traveller.getVector(model))

    ### Plot the catchment ###.
    if plot: plot_catchment(connected, tr, tc, tb)

if (__name__ == "__main__"):
    main()
