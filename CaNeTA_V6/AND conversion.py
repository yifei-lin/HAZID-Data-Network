# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 11:32:38 2024

@author: uqylin13
"""

#### AND gate conversion
def group_AND_gate_nodes(adj_matrix, grouped_nodes, ungrouped, already_grouped):
    n = len(adj_matrix)
    grouped_set = set()
    
    for i in already_grouped:
        if isinstance(i, list):  # Check if the element is a list
            for j in i:
                grouped_set.add(j)
        else:
            grouped_set.add(i)

    # Iterate through the matrix to find AND gate connections and group nodes
    for i in range(n):
        if i in grouped_set:
            continue

        for j in range(i + 1, n):
            if j in grouped_set:
                continue

            # Check if both nodes i and j point to the same node with AND relationship
            common_targets = [k for k in range(n) if adj_matrix[i][k] > 1 and adj_matrix[j][k] > 1]
            if common_targets:
                grouped_nodes.append((i, j))
                grouped_set.add(i)
                grouped_set.add(j)
                break

    # Update ungrouped nodes
    ungrouped -= grouped_set

    return grouped_nodes, list(ungrouped)

def AND_Gate_Conversion(original_matrix, adj_matrix, grouped_nodes, ungrouped, already_grouped, node_mapping):
    
    grouped_nodes, ungrouped = group_AND_gate_nodes(adj_matrix, grouped_nodes, ungrouped, already_grouped)
    print('getting_AND_grouped_nodes: ' + str(grouped_nodes))
    print('getting_AND_ungrouped_nodes: ' + str(ungrouped))
    
    n = len(adj_matrix)
    grouped_node_count = len(grouped_nodes)
    new_n = n - grouped_node_count  # Decrease size for each grouped pair

    # Create a mapping from old to new node indices                         
    node_mapping = {}
    new_index = 0
    flattened_grouped_nodes = flatten_grouped_nodes(grouped_nodes)
    
    if len(already_grouped) == 0:
        for i in range(n):
            if i in flattened_grouped_nodes:
                if i not in node_mapping:
                    node_mapping[i] = new_index // 2  # Grouped nodes get the same new index
                    new_index += 1
            else:
                node_mapping[i] = new_index - grouped_node_count
                new_index+=1
        print(node_mapping)
    
        # Create new adjacency matrix
        new_adj_matrix = np.zeros((new_n, new_n))
        for i in range(n):
            new_i = node_mapping[i]
            
            for j in range(n):
                new_j = node_mapping[j]
                
                if adj_matrix[i][j] > 1:
                    # Sum the weights to the new matrix and subtract 1
                    new_adj_matrix[new_i][new_j] = max(new_adj_matrix[new_i][new_j], adj_matrix[i][j] - 1)
                if adj_matrix[i][j] == 1:
                    new_adj_matrix[new_i][new_j] = 1
    
    if len(already_grouped) > 0:
        n = len(original_matrix)
        add_on = []
        for value_to_remove in flattened_grouped_nodes:
            for i in node_mapping.keys():
                if node_mapping[i] == value_to_remove:
                    add_on.append(i)
            node_mapping = {k: v for k, v in node_mapping.items() if v != value_to_remove}
        new_index = max(node_mapping.values())
      
        for i in range(len(add_on)):
            node_mapping[add_on[i]] = i//2 + new_index + 1 # Grouped nodes get the same new index
        print(node_mapping)
        new_adj_matrix = np.zeros((new_n, new_n))
                
        for i in range(n):
            new_i = node_mapping[i]
            
            for j in range(n):
                new_j = node_mapping[j]
                if original_matrix[i][j] > 1:
                    
                    print(new_i, new_j)
                    
                    if new_i != new_j:
                        new_adj_matrix[new_i][new_j] = max(new_adj_matrix[new_i][new_j], original_matrix[i][j] - 1)
    final_grouped_nodes = set()
    final_ungrouped = set()
    for i in grouped_nodes:
        for k in i:
            final_grouped_nodes.add(node_mapping[k])
    for j in ungrouped:
        final_ungrouped.add(node_mapping[j])
    
    return new_adj_matrix, grouped_nodes, ungrouped, list(final_grouped_nodes), final_ungrouped, node_mapping