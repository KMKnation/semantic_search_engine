from scipy.spatial import distance
from sklearn.cluster import KMeans


c = KMeans()

d = distance.euclidean(p1, p2)
print("Euclidean distance: ", d)



