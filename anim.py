#Importing modules
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np
import random
from geopy import distance
from utils.usMap import usMap
import cartopy.crs as ccrs

# Customer data import
path = "Uber Freight Engineering - Customer Demands Business Case.xlsx"
df = pd.read_excel(path)

# All coors are in (lattiude, longitude) order

def initialization_method(k:int, method:str, points:tuple[float,float]) -> list[tuple[float, float]]:
    # Setting range
    x_range = (min([n[1] for n in points]), max([n[1] for n in points]))
    y_range = (min([n[0] for n in points]), max([n[0] for n in points]))
    
    #Init clusters
    centroids = []
    
    if method == "Random":
        for _ in range(k):
            lat = random.uniform(y_range[0], y_range[1])
            lon = random.uniform(x_range[0], x_range[1])
            centroids.append((lat,lon))

    #TODO: Implement forgy

    return centroids

def weight(point:tuple[float,float], weight:int, centroid:tuple[float, float]) -> float:
    # For geodesic distances and counting the number of shipments
    return (weight * distance.distance(point, centroid).miles)

    
def calculate_centroid(points:list[tuple[float,float]]) -> tuple[float,float]:
    # Mean of all points approach
    mean_lat = sum([coors[0] for coors in points])/len(points)
    mean_lon = sum([coors[1] for coors in points])/len(points)

    return (mean_lat, mean_lon)

# Turning function into a generator
def k_means_cluster_generator(k:int, points:list[tuple[float, float]], weights:list[int]) -> tuple[list[tuple[float, float]], list[tuple[float,float]]]:
    # Initialization: choose k centroids by method
    method = ["Random", "Forgy"]
    centroids = initialization_method(k, method[0], points)

    # Initialize cluster list
    clusters = [[] for _ in range(k)]

    # Loop until convergence
    converged = False
    while not converged:
        # Clear previous clusters
        clusters = [[] for _ in range(k)]

        # Assign each point to the "closest" centroid
        for i, point in enumerate(points):
            weights_to_each_centroid = [weight(point, weights[i], centroid) for centroid in centroids]
            cluster_assignment = np.argmin(weights_to_each_centroid) # Selects the lightest centroid 
            clusters[cluster_assignment].append(point)

        yield clusters, centroids

        # Calculate new centroids
        #   (the standard implementation uses the mean of all points in a cluster to determine the new centroid)
        new_centroids = [calculate_centroid(cluster) for cluster in clusters]

        converged = (new_centroids == centroids)
        centroids = new_centroids


fig, ax = usMap()

# Static customer scatter
scatter = ax.scatter(
    x=df['Longitude'],
    y=df['Latitude'],
    c=df['SHIPMENTS'],
    s=df['SHIPMENTS'] * 0.5,
    cmap='viridis',
    alpha=0.5,
    transform=ccrs.PlateCarree(),
    zorder=3
)
plt.colorbar(scatter, ax=ax, label='Shipments')

# Dynamic elements
centroid_points, = ax.plot([], [], "o", color="red", transform=ccrs.PlateCarree(),
                        zorder=4, markersize=8, markeredgecolor="black", markeredgewidth=1)  # Centroids
lines = []
iter_text = ax.text(.01, .99, '', ha='left', va='top', transform=ax.transAxes, fontsize=12)
iteration = 1

def init():
    centroid_points.set_data([], [])
    return [centroid_points]

def update(data):
    global lines, iteration
    clusters, centroids = data

    # Update centroids
    lons = [c[1] for c in centroids]
    lats = [c[0] for c in centroids]
    centroid_points.set_data(lons, lats)

    # Clear previous lines
    for line in lines:
        line.remove()
    lines = []

    # Plot lines connecting customers to centroids
    for i, cluster in enumerate(clusters):
        for customer in cluster:
            line, = ax.plot(
                [customer[1], centroids[i][1]],
                [customer[0], centroids[i][0]],
                color='gray', linewidth=0.5, alpha=0.7,
                transform=ccrs.PlateCarree(), zorder=2
            )
            lines.append(line)
    
    iter_text.set_text(f"Iteration: {iteration}")
    iteration += 1

    return [centroid_points] + lines + [iter_text]

# Create generator
gen = k_means_cluster_generator(k=2, points=list(zip(df['Latitude'], df['Longitude'])), weights=df['SHIPMENTS'].tolist())

ani = animation.FuncAnimation(
    fig, update, frames=gen,
    init_func=init, blit=False, interval=1000, repeat=False, save_count=100
)

fig.set_size_inches(12, 6)
fig.set_dpi(150)
plt.title('Weighted K-Means Clustering', fontsize=14, pad=20)
ani.save("Weighted_K-Means_iters.gif")
plt.show()