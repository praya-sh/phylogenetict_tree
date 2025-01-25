import numpy as np

class UPGMAClusterer:
    def __init__(self, distance_matrix):
        """
        Initialize the UPGMA clusterer with a distance matrix
        
        Args:
            distance_matrix (numpy.ndarray): Symmetric distance matrix between sequences
        """
        self.original_matrix = np.array(distance_matrix, dtype=float)
        self.matrix = self.original_matrix.copy()
        self.num_sequences = len(self.matrix)
        
        # Initialize cluster tracking
        self.clusters = [f"Seq_{i+1}" for i in range(self.num_sequences)]
        self.cluster_sizes = np.ones(self.num_sequences, dtype=int)
        self.cluster_mapping = {}
    
    def find_minimum_distance(self):
        """
        Find the minimum distance in the matrix, excluding diagonal and self-distances
        
        Returns:
            tuple: Indices of the two closest clusters
        """
        # Create a mask to ignore diagonal and redundant entries
        mask = np.triu(np.ones_like(self.matrix, dtype=bool), k=1)
        masked_matrix = np.ma.masked_array(self.matrix, mask=~mask)
        
        # Find the indices of the minimum distance
        min_index = np.unravel_index(
            masked_matrix.argmin(), 
            masked_matrix.shape
        )
        return min_index
    
    def merge_clusters(self, index1, index2):
        """
        Merge two clusters and update distance matrix
        
        Args:
            index1 (int): Index of first cluster to merge
            index2 (int): Index of second cluster to merge
        """
        # Calculate new cluster size using NumPy arrays
        new_size = self.cluster_sizes[index1] + self.cluster_sizes[index2]
        
        # Create new cluster name
        new_cluster_name = f"Cluster_{len(self.clusters) + 1}"
        
        # Store cluster merge information
        self.cluster_mapping[new_cluster_name] = {
            'left': self.clusters[index1],
            'right': self.clusters[index2],
            'left_distance': self.matrix[index1, index2] / 2,
            'right_distance': self.matrix[index1, index2] / 2
        }
        
        # Update distance matrix
        new_distances = np.zeros(len(self.matrix) - 1)
        for i in range(len(self.matrix)):
            if i != index1 and i != index2:
                # UPGMA average linkage calculation
                new_dist = (
                    self.matrix[index1, i] * self.cluster_sizes[index1] + 
                    self.matrix[index2, i] * self.cluster_sizes[index2]
                ) / new_size
                new_distances[i if i < min(index1, index2) else i-1] = new_dist
        
        # Reconstruct matrix and cluster tracking
        self.matrix = np.delete(self.matrix, [index1, index2], axis=0)
        self.matrix = np.delete(self.matrix, [index1, index2], axis=1)
        
        # Add new row and column
        self.matrix = np.pad(self.matrix, ((0, 1), (0, 1)), mode='constant')
        self.matrix[-1, :-1] = new_distances[:-1]
        self.matrix[:-1, -1] = new_distances[:-1]
        
        # Update clusters and sizes using lists and NumPy array
        self.clusters.append(new_cluster_name)
        self.cluster_sizes = np.delete(self.cluster_sizes, [index1, index2])
        self.cluster_sizes = np.append(self.cluster_sizes, new_size)
        
        # Remove merged clusters
        del self.clusters[max(index1, index2)]
        del self.clusters[min(index1, index2)]
    
    def cluster(self):
        """
        Perform complete UPGMA clustering
        
        Returns:
            dict: Cluster mapping representing the hierarchical clustering
        """
        while len(self.clusters) > 1:
            # Find minimum distance indices
            index1, index2 = self.find_minimum_distance()
            
            # Merge the clusters
            self.merge_clusters(index1, index2)
        
        return self.cluster_mapping
    
    def get_newick_tree(self):
        """
        Convert cluster mapping to Newick tree format
        
        Returns:
            str: Newick tree representation
        """
        def build_newick(cluster_name):
            # Recursive Newick tree construction
            if cluster_name in [f"Seq_{i+1}" for i in range(self.num_sequences)]:
                return cluster_name
            
            node = self.cluster_mapping[cluster_name]
            left = build_newick(node['left'])
            right = build_newick(node['right'])
            
            return f"({left}:{node['left_distance']},{right}:{node['right_distance']})"
        
        # Get the final cluster (root of the tree)
        final_cluster = self.clusters[0]
        return build_newick(final_cluster) + ";"

# Example usage
def main():
    # Example distance matrix
    distance_matrix = np.array([
        [0, 2, 3, 4],
        [2, 0, 5, 6],
        [3, 5, 0, 1],
        [4, 6, 1, 0]
    ])
    
    # Perform UPGMA clustering
    clusterer = UPGMAClusterer(distance_matrix)
    cluster_mapping = clusterer.cluster()
    
    # Print cluster mapping and Newick tree
    print("Cluster Mapping:")
    for cluster, details in cluster_mapping.items():
        print(f"{cluster}: {details}")
    
    print("\nNewick Tree:")
    print(clusterer.get_newick_tree())

if __name__ == "__main__":
    main()