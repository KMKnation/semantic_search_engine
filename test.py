from scipy.spatial import distance
from sklearn.cluster import KMeans


c = KMeans()
p1 = [1,2,3]
p2 = [1,2,3]
d = distance.euclidean(p1, p2)
print("Euclidean distance: ", d)



