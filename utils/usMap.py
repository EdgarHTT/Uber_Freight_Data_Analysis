"""
Loads an USA states map with a Plate Carree projection
Innitiate by assigning the figure and axes
figure, axes = usMap()
plt.show()
"""
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
from shapely.geometry import MultiPolygon

# States and Provinces
def states(ax):
    # Load states/provinces shapefile
    shapename = 'admin_1_states_provinces_lakes'
    states_shp = shpreader.natural_earth(resolution='110m', category='cultural', name=shapename)
    
    # Creating a mask for the heatmap
    states = list(shpreader.Reader(states_shp).geometries())

    # Some states have multipoligons within them causing problems
    all_polygons = []
    for geom in states:
        if geom.is_empty:
            continue
        if geom.geom_type == 'MultiPolygon':
            # Extract individual polygons
            all_polygons.extend(list(geom.geoms))
        elif geom.geom_type == 'Polygon':
            all_polygons.append(geom)
            
    # Combining all state geometries into a multipoligon for masking
    # Making it global so it looks clean
    global usa_geoms
    usa_geoms = MultiPolygon(all_polygons)
    
    for state in shpreader.Reader(states_shp).records():
    
        facecolor = 'none' #Transparent
        edgecolor = 'black'
    
        ax.add_geometries(
            [state.geometry],
            crs=ccrs.PlateCarree(),
            facecolor=facecolor,
            edgecolor=edgecolor,
            linewidth=0.4,
            zorder=2 # to the back
        )

# Basic US map with states and provinces
def usMap():
    # Init plot
    fig = plt.figure()
    
    # Setup LambertConformal projection map of USA
    ax = fig.add_subplot(1,1,1, projection=ccrs.LambertConformal())
    
    # USA coordinates range from -124.67 to -66.95 lon, 25.84 to 49.38 lat.
    ax.set_extent([-125, -66.5, 20, 50], crs=ccrs.Geodetic())

    # Adding States/Provinces
    states(ax)
    
    return fig, ax