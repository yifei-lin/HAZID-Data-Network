from tkinter import *
from tkinter import filedialog
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from PIL import Image
from scipy.integrate import simps
from scipy.stats import skew
import xlsxwriter
import re
import tkinter as tk
import matplotlib
from datetime import datetime
from tqdm import tqdm
import seaborn as sns; sns.set_theme(color_codes=True)


matplotlib.use('TkAgg')
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Matrix():
    def __init__(self, excel_name, node_weight: dict, node_ID: dict):
        """
        Construct an adjacency matrix with node_id,node_weight saved.

        Parameters:
        excel_name: A string shows the file needs to be read.
        node_weight: An emtpy Dictionary at initial, contains nodes weighting info.
        node_ID: An emtpy Dictionary at initial, contains nodes ID.
        """
        self._excel_name = excel_name
        self._node_weight = node_weight
        self._node_ID = node_ID
        self._df = self.read_sheet(self._excel_name)
        self._gather_list = []
        self._adjacency_matrix = []
        self._removed_nodes = []
        self.gcm()

    def read_sheet(self, file_name, skiprows=0):
        """(pd.dataframe): Returns the first sheet of the excel file"""
        ## Read the input excel sheet with file_name given and return a dataframe.
        ## Pandas in use
        df = pd.read_excel(file_name, skiprows=skiprows)
        return df

    def checkSame(self, nodeName, dictionaryName):
        """(Boolean): Returns true while nodeName's lower cases equals any keys inside input dictionary.
                      Returns false while no matches.
        """
        for i in dictionaryName.keys():
            if nodeName.lower() == i.lower():
                return True
        return False

    def splitWeight(self, nodeWeight, node, weight, bracketOR, bracketAND):
        """ Split input node string and weight them.

        Parameters:
            nodeWeight (Dictionary): Contains Node elements correspond to their node_ID
            node (String): Excel block elements contains node element (Usually contains more than one node element)
            weight (Int): Initial set to zero.
            bracketOR(Int): Initial set to zero.
            bracketAND(Int): Initial set to zero.
        """
        if ' AND ' not in node and ' OR ' not in node:
            if '(' in node and ')' not in node:
                nodesDeviation = node.split('(')[1]
                nodeWeight[nodesDeviation] = weight
            elif ')' in node and '(' not in node:
                nodesDeviation = node.split(')')[0]
                nodeWeight[nodesDeviation] = weight
            elif '(' in node and ')' in node:
                nodesDeviation = node.split('(')[1]
                nodesDDeviation = nodesDeviation.split(')')[0]
                nodeWeight[nodesDDeviation] = weight
            else:
                nodeWeight[node] = weight
        if ' OR ' in node:
            if bracketOR == 0:
                ## split OR outside brackets
                a = re.split(r' OR \s*(?![^()]*\))', node)
                for i in a:
                    self.splitWeight(nodeWeight, i, weight, bracketOR + 1, bracketAND)
            elif bracketOR > 0:
                if '(' not in node:
                    nodesDeviation = node.split(' OR ')
                    for j in nodesDeviation:
                        self.splitWeight(nodeWeight, j, weight, bracketOR, bracketAND)
                else:
                    ## split AND outside brackets
                    a = re.split(r' AND \s*(?![^()]*\))', node)
                    for i in a:
                        if '(' in i:
                            nodesDeviation = i.split('(')[1]
                            nodesDDeviation = nodesDeviation.split(')')[0]
                            self.splitWeight(nodeWeight, nodesDDeviation, weight + len(a) - 1, bracketOR + 1,
                                             bracketAND + 1)
                        else:
                            self.splitWeight(nodeWeight, i, weight + len(a) - 1, bracketOR + 1, bracketAND + 1)
        if ' AND ' in node and ' OR ' not in node:
            if bracketAND == 0:
                ## split AND outside brackets
                a = re.split(r' AND \s*(?![^()]*\))', node)
                if len(a) == 1:
                    self.splitWeight(nodeWeight, str(a), weight, bracketOR, bracketAND + 1)
                else:
                    for i in a:
                        self.splitWeight(nodeWeight, i, weight + len(a) - 1, bracketOR, bracketAND + 1)
            elif bracketAND == 1:
                nodesDeviation = node.split(' AND ')
                for j in nodesDeviation:
                    self.splitWeight(nodeWeight, j, weight + len(nodesDeviation) - 1, bracketOR, bracketAND)

    def splitID(self, node, bracketOR, bracketAND,splitID_recursion_count=0):
        """ Split input node string and number them.

        Parameters:
            node (String): Excel block elements contains node element (Usually contains more than one node element)
            bracketOR(Int): Initial set to zero.
            bracketAND(Int): Initial set to zero.
        """
        if splitID_recursion_count>100:
            print("SplitID() node: {}".format(node))
            raise NameError("splitID() Recursion Error")
        count = 0
        if 'AND' not in node and 'OR' not in node:
            if '(' in node and ')' not in node:
                nodesDeviation = node.split('(')[1]
                if not self.checkSame(nodesDeviation, self._node_ID):
                    self._node_ID[nodesDeviation] = count + len(self._node_ID)
                    count += 1

            elif ')' in node and '(' not in node:
                nodesDeviation = node.split(')')[0]
                if not self.checkSame(nodesDeviation, self._node_ID):
                    self._node_ID[nodesDeviation] = count + len(self._node_ID)
                    count += 1

            elif '(' in node and ')' in node:
                nodesDeviation = node.split('(')[1]
                nodesDDeviation = nodesDeviation.split(')')[0]
                if not self.checkSame(nodesDDeviation, self._node_ID):
                    self._node_ID[nodesDDeviation] = count + len(self._node_ID)
                    count += 1

            else:
                if not self.checkSame(node, self._node_ID):
                    a = len(self._node_ID)
                    self._node_ID[node] = count + a
                    count += 1

        if 'OR' in node:
            if bracketOR == 0:
                ## split OR outside brackets
                a = re.split(r' OR \s*(?![^()]*\))', node)
                for i in a:
                    self.splitID(i, bracketOR + 1, bracketAND,splitID_recursion_count+1)
            elif bracketOR == 1:
                nodesDeviation = node.split(' OR ')
                for j in nodesDeviation:
                    self.splitID(j, bracketOR, bracketAND,splitID_recursion_count+1)
        if 'AND' in node and 'OR' not in node:
            if bracketAND == 0:
                ## split AND outside brackets
                a = re.split(r' AND \s*(?![^()]*\))', node)
                if len(a) == 1:
                    self.splitID(str(a), bracketOR, bracketAND + 1,splitID_recursion_count+1)
                else:
                    for i in a:
                        self.splitID(i, bracketOR, bracketAND + 1,splitID_recursion_count+1)
            elif bracketAND == 1:
                nodesDeviation = node.split(' AND ')
                for j in nodesDeviation:
                    self.splitID(j, bracketOR, bracketAND,splitID_recursion_count+1)

    def splitIDD(self, node_IDD, node, bracketOR, bracketAND):
        """ Split input node string and number them.

        Parameters:
            node_IDD(Dictionary): Node elements correspond to their IDs (Rows)
            node (String): Excel block elements contains node element (Usually contains more than one node element)
            bracketOR(Int): Initial set to zero.
            bracketAND(Int): Initial set to zero.
        """
        count = 0
        if 'AND' not in node and 'OR' not in node:
            if '(' in node and ')' not in node:
                nodesDeviation = node.split('(')[1]
                if not self.checkSame(nodesDeviation, node_IDD):
                    node_IDD[nodesDeviation] = count + len(node_IDD)
                    count += 1

            elif ')' in node and '(' not in node:
                nodesDeviation = node.split(')')[0]
                if not self.checkSame(nodesDeviation, node_IDD):
                    node_IDD[nodesDeviation] = count + len(node_IDD)
                    count += 1

            elif '(' in node and ')' in node:
                nodesDeviation = node.split('(')[1]
                nodesDDeviation = nodesDeviation.split(')')[0]
                if not self.checkSame(nodesDDeviation, node_IDD):
                    node_IDD[nodesDDeviation] = count + len(node_IDD)
                    count += 1

            else:
                if not self.checkSame(node, node_IDD):
                    node_IDD[node] = count + len(node_IDD)
                    count += 1

        if 'OR' in node:
            if bracketOR == 0:
                ## split OR outside brackets
                a = re.split(r' OR \s*(?![^()]*\))', node)
                for i in a:
                    self.splitIDD(node_IDD, i, bracketOR + 1, bracketAND)
            elif bracketOR == 1:
                nodesDeviation = node.split(' OR ')
                for j in nodesDeviation:
                    self.splitIDD(node_IDD, j, bracketOR, bracketAND)
        if 'AND' in node and 'OR' not in node:
            if bracketAND == 0:
                ## split AND outside brackets
                a = re.split(r' AND \s*(?![^()]*\))', node)
                if len(a) == 1:
                    self.splitIDD(node_IDD, str(a), bracketOR, bracketAND + 1)
                else:
                    for i in a:
                        self.splitIDD(node_IDD, i, bracketOR, bracketAND + 1)
            elif bracketAND == 1:
                nodesDeviation = node.split(' AND ')
                for j in nodesDeviation:
                    self.splitIDD(node_IDD, j, bracketOR, bracketAND)

    def gatherNode(self, list_cus, causeNode, times):
        """ Create the input 'list_cus' as a list storing node relations.
            This list is mainly used for nodes elmination.

        Parameters:
            list_cus(List): Initial empty list, with [a,b] showing a causes b.
            causeNode (String): Excel block elements contains node element (Usually contains more than one node element)
            times(Int): Initial set to zero.
        """
        list_1 = []
        list_22 = []
        if '(' not in causeNode and ')' not in causeNode:
            if 'AND' in causeNode:
                a = causeNode.split(' AND ')
                for i in a:
                    list_1.append(i)
                list_cus.append(list_1)
            elif 'OR' in causeNode:
                a = causeNode.split(' OR ')
                for i in a:
                    list_1.append(i)
                    list_cus.append(list_1)
                    list_1 = []
            else:
                list_1.append(causeNode)
                list_cus.append(list_1)
        if '(' in causeNode:
            ## split OR outside brackets
            a = re.split(r' OR \s*(?![^()]*\))', causeNode)
            if len(a) == 1:
                for x in a:
                    if 'OR' in x:
                        ## split AND outside brackets
                        b = re.split(r' AND \s*(?![^()]*\))', causeNode)
                        for i in b:
                            nodesDeviation = i.split('(')[1]
                            nodesDDeviation = nodesDeviation.split(')')[0]
                            if 'OR' in nodesDDeviation:
                                c = nodesDDeviation.split(' OR ')
                                for j in c:
                                    list_22.append(j)
                                list_1.append(list_22)
                            elif 'AND' in nodesDDeviation:
                                c = nodesDDeviation.split(' AND ')
                                for j in c:
                                    list_1.append(j)
                            else:
                                list_1.append(nodesDDeviation)
                        list_cus.append(list_1)
                    else:
                        ## split AND outside brackets
                        b = re.split(r' AND \s*(?![^()]*\))', x)
                        for y in b:
                            nodesDeviation = y.split('(')[1]
                            nodesDDeviation = nodesDeviation.split(')')[0]
                            if 'AND' in nodesDDeviation:
                                c = nodesDDeviation.split(' AND ')
                                for z in c:
                                    list_1.append(z)
                            else:
                                list_1.append(nodesDDeviation)
                        list_cus.append(list_1)
            elif len(a) != 1:
                if times == 0:
                    for i in a:
                        self.gatherNode(list_cus, i, times + 1)
                else:
                    if '(' in i:
                        nodesDeviation = i.split('(')[1]
                        nodesDDeviation = nodesDeviation.split(')')[0]
                        self.gatherNode(list_cus, nodesDDeviation, times)
                    else:
                        list_1.append(i)
                        list_cus.append(list_1)

    def deleteNode(self, node_no: list):
        """ Delete the node inside the node_no from adjacency matrix.

        Parameters:
            node_no(List): Nodes waited to be eliminated.
        """
        gather_list_two = self._gather_list.copy()
        if len(node_no) == 0:
            self._gather_list = gather_list_two
        else:
            for j in range(len(self._adjacency_matrix)):
                ##The relations showing nodes point to the eliminated node should be removed.
                self._adjacency_matrix[j][int(node_no[0])] = 0
            for mid_list in self._gather_list:
                ## Check mid_list contains all integer or not.
                if all(isinstance(item, int) for item in mid_list[0]):
                    if int(node_no[0]) in mid_list[0]:
                        list_1 = mid_list[0]
                        for jj in list_1:
                            self._adjacency_matrix[jj][mid_list[1]] = 0
                        node_no.append(mid_list[1])
                        gather_list_two.remove(mid_list)
                else:
                    if int(node_no[0]) in mid_list[0]:
                        for i in mid_list[0]:
                            if isinstance(i, int):
                                self._adjacency_matrix[i][mid_list[1]] = 0
                            if isinstance(i, list):
                                for list_item in i:
                                    self._adjacency_matrix[list_item][mid_list[1]] = 0
                        ## The relations showing nodes caused by eliminated nodes should also be removed.
                        node_no.append(mid_list[1])
                        gather_list_two.remove(mid_list)
                    elif int(node_no[0]) not in mid_list[0]:
                        for i in mid_list[0]:
                            if isinstance(i, list):
                                if len(i) == 0:
                                    node_no.append(mid_list[1])
                                    gather_list_two.remove(mid_list)
                                else:
                                    for list_item_1 in i:
                                        if list_item_1 == int(node_no[0]):
                                            self._adjacency_matrix[list_item_1][mid_list[1]] = 0
                                            i.remove(list_item_1)
            node_no.pop(0)
            for mid_list in gather_list_two:
                for node_check in node_no:
                    if mid_list[1] == node_check:
                        node_no.remove(node_check)
            self._gather_list = gather_list_two
            self.deleteNode(node_no)

    def gcm(self):
        """ Create the Adjacency Matrix."""
        df = self._df
        name = []
        for col in list(df.columns):
            name.append(col)
        df = df[[name[0], name[1], name[2]]]
        for index, row in df.iterrows():
            
            try:
                if row[name[0]] != 'None':
                    self.splitID(row[name[0]].rstrip(), 0, 0)
                if row[name[1]] != 'None':
                    self.splitID(row[name[1]].rstrip(), 0, 0)
                if row[name[2]] != 'None':
                    self.splitID(row[name[2]].rstrip(), 0, 0)
            except:
                print(index)
                print(name[0])
                print(row[name[0]])
                print(name[1])
                print(row[name[1]])
                print(name[2])
                print(row[name[2]])
                raise NameError("Gordon")
                
        ## Set initial size of the adjacency matrix.
        adjacency_matrix = np.zeros((len(self._node_ID), len(self._node_ID)))
        for index, row in df.iterrows():

            ## The second column and the first column
            node_Weight1 = {}
            node_IDD1 = {}
            list_cus = []

            ##Get node weight
            self.splitWeight(node_Weight1, row[name[1]].rstrip(), 1, 0, 0)
            ##Get node ID
            self.splitIDD(node_IDD1, row[name[0]].rstrip(), 0, 0)
            ##split node for delete_node function
            self.gatherNode(list_cus, row[name[1]].rstrip(), 0)
            count = 0
            count1 = 0
            for a in list_cus:
                for b in a:
                    if isinstance(b, str):
                        for k in self._node_ID.keys():
                            if b.lower() == k.lower():
                                a[count] = self._node_ID[k]
                                count += 1
                    elif isinstance(b, list):
                        for kk in b:
                            for k in self._node_ID.keys():
                                if kk.lower() == k.lower():
                                    a[count][count1] = self._node_ID[k]
                                    count1 += 1
                        count += 1
                count = 0
            ## Create the relationship list (gather_list) mainly used for nodes elimination
            for aa in node_IDD1.keys():
                for bb in self._node_ID.keys():
                    if aa.lower() == bb.lower():
                        cc = self._node_ID[bb]
                        for xx in list_cus:
                            list_2 = [xx, cc]
                            self._gather_list.append(list_2)
            ## start creating adjacency matrix
            for i in node_Weight1.keys():
                for k in self._node_ID.keys():
                    if i.lower() == k.lower():
                        x = self._node_ID[k]
                        for j in node_IDD1.keys():
                            for l in self._node_ID.keys():
                                if j.lower() == l.lower():
                                    y = self._node_ID[l]
                                    adjacency_matrix[x, y] = node_Weight1[i]

            ## The first column and the third column
            node_Weight2 = {}
            node_IDD2 = {}
            list_cus_1 = []
            self.splitWeight(node_Weight2, row[name[0]].rstrip(), 1, 0, 0)
            self.splitIDD(node_IDD2, row[name[2]].rstrip(), 0, 0)
            self.gatherNode(list_cus_1, row[name[0]].rstrip(), 0)
            count = 0
            for a in list_cus_1:
                for b in a:
                    for k in self._node_ID.keys():
                        if isinstance(b, str):
                            if b.lower() == k.lower():
                                a[count] = self._node_ID[k]
                                count += 1
                        elif b is list:
                            for kk in b:
                                if kk.lower() == k.lower():
                                    a[count] = self._node_ID[k]
                                    count += 1
                count = 0
            ## Create the relationship list (gather_list) mainly used for nodes elimination
            for aa in node_IDD2.keys():
                for bb in self._node_ID.keys():
                    if aa.lower() == bb.lower():
                        cc = self._node_ID[bb]
                        for xx in list_cus_1:
                            list_2 = [xx, cc]
                            self._gather_list.append(list_2)
            ## start creating adjacency matrix
            for m in node_Weight2.keys():
                for o in self._node_ID.keys():
                    if m.lower() == o.lower():
                        u = self._node_ID[o]
                        for n in node_IDD2.keys():
                            for p in self._node_ID.keys():
                                if n.lower() == p.lower():
                                    v = self._node_ID[p]
                                    adjacency_matrix[u, v] = node_Weight2[m]
        self._adjacency_matrix = adjacency_matrix

    def adjacency_matrix(self):
        return self._adjacency_matrix

    def get_gather_list(self):
        return self._gather_list

    def get_node_ID(self):
        return self._node_ID


class digraphPlot(tk.Canvas, tk.Frame):

    def __init__(self, master, delete_node=[], node_weight={}, node_ID={}):
        """
        Construct a view from a Matrix.
        Parameters:
        master (tk.Widget): Widget within which the frame is placed.
        delete_node(list): An emtpy list at initial, contains nodes need to be deleted.
        node_weight(Dictionary): An emtpy Dictionary at initial, contains nodes weighting info.
        node_ID(Dictionary): An emtpy Dictionary at initial, contains nodes ID.
        """
        super().__init__(master)

        self._node_weight = node_weight
        self._node_ID = node_ID
        self._delete_node = delete_node
        self._master = master
        self._excel_name = self.load_excel()
        print("[{}] Creating adjacency Matrix".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        self._matrix = Matrix(self._excel_name, self._node_ID, self._node_weight)
        self._adjacency_matrix = self._matrix.adjacency_matrix()
        self._node_ID = self._matrix.get_node_ID()
        self._digraph_normal = self.get_Digraph()
        self._pos = nx.nx_agraph.graphviz_layout(self._digraph_normal)
        self.add_menu()
        self._frame_one = tk.Frame(self._master, bg='grey', width=3000, height=1800)
        self._frame_one.pack(side=tk.LEFT, expand=1, anchor=tk.W)
        self.plot_Digraph_initial()
        self._frame_two = tk.Frame(self._master, bg='grey')
        self._frame_two.pack()
        self.options = ["Degree", "In_Degree", "Out_Degree", "Strength", "In_Strength", "Out_Strength", "Eigenvector", 
                                 "In_Closeness", "Out_Closeness", "Betweenness", "Relative_Likelihood", "Causal_Contribution"]
        self._frame_two = tk.Frame(self._master, bg='grey')
        self._frame_two.pack()
        self.add_button()
        self.clicked = StringVar()
        self.clicked.set("Degree")
        drop = OptionMenu( self._frame_two , self.clicked , *self.options)
        drop.config(width=100)
        drop.pack()
        button_colormap = Button( self._frame_two , text = "colormap" , command = self.show_colormap, width=100).pack()
        button_distribution = Button( self._frame_two , text = "distribution" , command = self.show_distribution, width=100).pack()
        button_robustness = Button( self._frame_two , text = "robustness_connected_remaining", command = self.show_robustness_connected, width=100).pack()
        button_robustness_remaining = Button( self._frame_two , text = "robustness_total_remaining", command = self.show_robustness_remaining, width=100).pack()
        print("[{}] add_button()".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        
        self._entry = tk.Entry(self._frame_two, font=60, relief='flat', width=100, bg="#33B5E5")
        self._entry.pack()
        self._entry.focus_set()
        self._buttonEntry = tk.Button(self._frame_two, text="Remove", width=100)
        self._buttonEntry.bind("<Button-1>", lambda evt: self.entryValueRemove())
        self._buttonEntry.pack()
        button_random = Button( self._frame_two , text = "random_robustness", command = self.start_random_robustness, width=100).pack()
        self._largest_component = []
        self._deleted_node = []
        self._node_neighbor = self.neighbor_of_nodes()
        self._number_of_remaining_nodes = []
        self._largest_connected_component = []
        self._node_left = []
        self._total_node = []
        for j in range(0, 320):
            self._total_node.append(j)
        print("\n[{}] finished digraphPlot init()".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))

    def get_color(self,k):
		# Yifei's original colour list
        color_list = ['red','blue','green','yellow','black','purple','grey','orange','fuchsia','olive','cyan','brown']
		
        # 12 Qualitative Colours from Color Brewer
		# https://colorbrewer2.org/#type=qualitative&scheme=Paired&n=12
        # color_list=['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99','#b15928']
        
        # Use CSS Colors
        # color_list=list(mcolors.CSS4_COLORS.keys())
        
        if k>=len(color_list):
            k=len(color_list)-1
        return(color_list[k])
    
    def add_menu(self):
        """Add the menu function in the master widget."""
        menubar = tk.Menu(self._master)
        self._master.config(menu=menubar)
        filemenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='File', menu=filemenu)
        filemenu.add_command(label='Load Excel', command=self.re_excel)
        filemenu.add_command(label='Save Matrix', command=self.save_matrix)
        filemenu.add_command(label='Quit', command=self.quit)

        self._filename = None

    def load_excel(self):
        """Select the excel file under same direction with this file"""
        self._filename = filedialog.askopenfilename(filetypes=[("Excel or CSV files", ".xlsx .xls .csv")])
        # If file exists
        if self._filename:
            self._master.title(self._filename)
            self._excel_name = self._filename
            return self._filename
        
    def start_random_robustness(self):
        """Monte Carlo simulation"""
        stored_matrix = self._matrix
        stored_node_left = self._node_left
        for i in range(0, len(self._adjacency_matrix)):
            self._node_left.append(i)
        area = 10000000
        a = 0
        final_left_nodes = []
        for i in range(1):
            ### keep run until the simulation time has reached
            b = len(self._digraph_normal)
            while b != 0:
                
                nodeID = int(np.random.choice(self._node_left))
                nodeID_list = [nodeID]
                self._node_left.remove(nodeID)
                if len(self._number_of_remaining_nodes) > 1:
                    if self._number_of_remaining_nodes[-1] != len(self._digraph_normal):
                        self._number_of_remaining_nodes.append(len(self._digraph_normal))
                else:
                    self._number_of_remaining_nodes.append(len(self._digraph_normal))
                self._matrix.deleteNode(nodeID_list)
                self._adjacency_matrix = self._matrix.adjacency_matrix()
                for i in self._node_left:
                    for j in self._node_left:
                        if self._adjacency_matrix[i][j] != 0:
                            final_left_nodes.append(i)
                            final_left_nodes.append(j)
                final_left_nodes = list(set(final_left_nodes))
                self._node_left = final_left_nodes
                final_left_nodes = []
                self._digraph_normal = self.get_Digraph()
                if len(self._digraph_normal) == 0:
                    break
            self._number_of_remaining_nodes.append(0)
            node_total = pd.Series(self._total_node, name='first_column')
            remaining_total = pd.Series(self._number_of_remaining_nodes,name='second_column')
            if len(self._number_of_remaining_nodes) < len(self._total_node):
                for i in range(len(self._total_node)-len(self._number_of_remaining_nodes)):
                    self._number_of_remaining_nodes.append(0)
            randomarray = {'first_column':self._total_node,
                                'second_column':self._number_of_remaining_nodes}
            df = pd.DataFrame(randomarray)
            
            df1 = pd.concat([node_total, remaining_total], axis=1)
            ### Store line to figure
            a += 1
            y=  df['second_column']
            x1 = df['first_column']
            y_1 = df1['second_column']
            x1_1 = df1['first_column']
            area1 = int(simps(np.array(y), x=np.array(x1)))
            if area > area1:
                area = area1
            if a == 1:
                plt.plot(x1_1, y_1, color = 'r', label = "Monte Carlo Simulation, least area under curve: " + str(area), alpha=0.25)
            if a != 1:
                plt.plot(x1_1, y_1, color = 'r', alpha=0.25)
            
            self._matrix = Matrix(self._excel_name, self._node_ID, self._node_weight)
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_ID = self._matrix.get_node_ID()
            self._digraph_normal = self.get_Digraph()
            print(len(self._digraph_normal))
            self._node_left = stored_node_left
            self._number_of_remaining_nodes = []
            for i in range(0, len(self._adjacency_matrix)):
                self._node_left.append(i)
        loc1 = ("Total_Robustness.xlsx")
        excel_data = pd.read_excel(loc1)

        total_robustness_new = {'Number of removed Nodes':excel_data['Number of removed Nodes'],
                                'Metric & Area Under Curve': excel_data['Metric & Area Under Curve'],
                            'Betweenness Area Under Curve: 13,623':excel_data['Number of Remaining Nodes Betweenness'],
                            'Degree Area Under Curve: 18,116': excel_data['Number of Remaining Nodes Degree']}
        df = pd.DataFrame(total_robustness_new)
        df.pivot(index='Number of removed Nodes', columns='Metric & Area Under Curve', values=['Betweenness Area Under Curve: 13,623','Degree Area Under Curve: 18,116'])
        print(df)
        plt.plot(excel_data['Number of removed Nodes'], excel_data['Number of Remaining Nodes Betweenness'], color='g', marker='.', label='Betweenness Area Under Curve: 13,623')
        plt.plot(excel_data['Number of removed Nodes'], excel_data['Number of Remaining Nodes Degree'], color='tab:purple', marker = '1', label='Degree Area Under Curve: 18,116')
        plt.plot(excel_data['Number of removed Nodes'], excel_data['Number of Remaining Nodes Strength'], color='m', marker = 'x', label='Strength Area Under Curve: 18,208')
        plt.plot(excel_data['Number of removed Nodes'], excel_data['Number of Remaining Nodes In Degree'], color='y', marker = 4,label='In Degree Area Under Curve: 20,023')
        plt.plot(excel_data['Number of removed Nodes'], excel_data['Number of Remaining Nodes In Strength'], color='b', marker = 6,label='In Strength Area Under Curve: 20,276')
        plt.plot(excel_data['Number of removed Nodes'], excel_data['Number of Remaining Nodes In Closeness'], color='tab:pink', marker = '|',label='In Closeness Area Under Curve: 23,803')
        plt.plot(excel_data['Number of removed Nodes'], excel_data['Number of Remaining Nodes Out Degree'], color='k', marker = '2',label='Out Degree Area Under Curve: 31,233')
        plt.plot(excel_data['Number of removed Nodes'], excel_data['Number of Remaining Nodes Out Strength'], color='c', marker = '+',label='Out Strength Area Under Curve: 31,663')
        plt.plot(excel_data['Number of removed Nodes'], excel_data['Number of Remaining Nodes Out Closeness'], color='tab:olive', marker = '*',label='Out Closeness Area Under Curve: 35,225')
        plt.title("Monte Carlo Simulation Compare Demo")
        plt.xlabel("Number of Removed Nodes")
        plt.ylabel("Number of Remaining Nodes")
        plt.legend()
        plt.show()
            
            
    def re_excel(self):
        """Select another excel file under same direction with this file
           Create Matrix, Redraw the frame and canvas.
        """
        filename = filedialog.askopenfilename()
        self._frame_one.destroy()
        self._frame_two.destroy()
        self._matrix = Matrix(filename, self._node_ID, self._node_weight)
        self._adjacency_matrix = self._matrix.adjacency_matrix()
        self._digraph_normal = self.get_Digraph()
        self._pos = nx.nx_agraph.graphviz_layout(self._digraph_normal)
        self._frame_one = tk.Frame(self._master, bg='grey', width=3000, height=1800)
        self._frame_one.pack(side=tk.LEFT, expand=1, anchor=tk.W)
        self.plot_Digraph_initial()
        self._frame_two = tk.Frame(self._master, bg='grey')
        self._frame_two.pack()
        self.options = ["Degree", "In_Degree", "Out_Degree", "Strength", "In_Strength", "Out_Strength", "Eigenvector", 
                                 "In_Closeness", "Out_Closeness", "Betweenness", "Relative_Likelihood", "Causal_Contribution"]
        self._frame_two = tk.Frame(self._master, bg='grey')
        self._frame_two.pack()
        self.add_button()
        self.clicked = StringVar()
        self.clicked.set("Degree")
        drop = OptionMenu( self._frame_two , self.clicked , *self.options)
        drop.config(width=100)
        drop.pack()
        button_colormap = Button( self._frame_two , text = "colormap" , command = self.show_colormap, width=100).pack()
        button_distribution = Button( self._frame_two , text = "distribution" , command = self.show_distribution, width=100).pack()
        button_robustness = Button( self._frame_two , text = "robustness_connected_remaining", command = self.show_robustness_connected, width=100).pack()
        button_robustness_remaining = Button( self._frame_two , text = "robustness_total_remaining", command = self.show_robustness_remaining, width=100).pack()
        print("[{}] add_button()".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        
        self._entry = tk.Entry(self._frame_two, font=60, relief='flat', width=100, bg="#33B5E5")
        self._entry.pack()
        self._entry.focus_set()
        self._buttonEntry = tk.Button(self._frame_two, text="Remove", width=100)
        self._buttonEntry.bind("<Button-1>", lambda evt: self.entryValueRemove())
        self._buttonEntry.pack()
        self._largest_component = []
        self._deleted_node = []
        self._node_neighbor = self.neighbor_of_nodes()
        self._number_of_remaining_nodes = []
        self._largest_connected_component = []
        
    def show_colormap(self):
        if self.clicked.get() == "Degree":
            self.plot_ColorMap(self.get_dict(self._digraph_normal.degree()), 'Degree')
        elif self.clicked.get() == "In_Degree":
            self.plot_ColorMap(self.get_dict(self._digraph_normal.in_degree()), 'In_Degree')
        elif self.clicked.get() == "Out_Degree":
            self.plot_ColorMap(self.get_dict(self._digraph_normal.out_degree()), 'Out_Degree')
        elif self.clicked.get() == "Strength":
            instrength_1 = self.det_instrength()
            outstrength_1 = self.det_outstrength()
            strength_1 = self.det_strength(instrength_1, outstrength_1)
            self.plot_ColorMap(strength_1, 'Strength')
        elif self.clicked.get() == "In_Strength":
            self.plot_ColorMap(self.det_instrength(), 'In_Strength')
        elif self.clicked.get() == "Out_Strength":
            self.plot_ColorMap(self.det_outstrength(), 'Out_Strength')
        elif self.clicked.get() == "Eigenvector":
            self.plot_ColorMap_eigen(nx.eigenvector_centrality(self._digraph_normal, max_iter=600), 'Eigenvector')
        elif self.clicked.get() == "In_Closeness":
            self.plot_ColorMap(nx.closeness_centrality(self._digraph_normal), 'In_Closeness')
        elif self.clicked.get() == "Out_Closeness":
            self.plot_ColorMap(nx.closeness_centrality(self._digraph_normal.reverse()), 'Out_Closeness')
        elif self.clicked.get() == "Betweenness":
            self.plot_ColorMap(nx.betweenness_centrality(self._digraph_normal),'Betweenness')
        elif self.clicked.get() == "Relative_Likelihood":
            self.plot_ColorMap(self.det_relative_likelihood(), 'Relative_Likelihood')
        elif self.clicked.get() == "Causal_Contribution":
            self.plot_ColorMap(self.det_causal_contribution(), 'Causal_Contribution')
            
    def show_distribution(self):
        if self.clicked.get() == "Degree":
            Indegree = self.det_indegree()
            Outdegree = self.det_outdegree()
            Degree = self.det_degree(Indegree, Outdegree)
            self.plot_distribution(Degree, 1, "Degree_Distribution")
        elif self.clicked.get() == "In_Degree":
            Indegree = self.det_indegree()
            self.plot_distribution(Indegree, 2,"In_Degree_Distribution")
        elif self.clicked.get() == "Out_Degree":
            Outdegree = self.det_outdegree()
            self.plot_distribution(Outdegree, 3,"Out_Degree_Distribution")
            
        elif self.clicked.get() == "Strength":
            strength_list = []
            instrength_1 = self.det_instrength()
            outstrength_1 = self.det_outstrength()
            strength_1 = self.det_strength(instrength_1, outstrength_1)
            for i in range(len(strength_1)):
                strength_list.append(strength_1.get(str(i)))
            self.plot_distribution(strength_list, 8, "Strength_Distribution")
            
        elif self.clicked.get() == "In_Strength":
            instrength_list = []
            instrength_1 = self.det_instrength()
            for i in range(len(instrength_1)):
                instrength_list.append(instrength_1.get(str(i)))
            self.plot_distribution(instrength_list, 9, "In_Strength_Distribution")
            
        elif self.clicked.get() == "Out_Strength":
            outstrength_list = []
            outstrength_1 = self.det_instrength()
            for i in range(len(outstrength_1)):
                outstrength_list.append(outstrength_1.get(str(i)))
            self.plot_distribution(outstrength_list, 10, "Out_Strength_Distribution")
            
        elif self.clicked.get() == "Eigenvector":
            Eigenvector_Centrality_values = []
            self.plot_distribution(self.det_eigenvector_one(Eigenvector_Centrality_values), 5, "Eigenvector_Distribution")
        elif self.clicked.get() == "In_Closeness":
            In_closeness_centrality_values = []
            self.plot_distribution(self.det_in_closeness_one(In_closeness_centrality_values), 4, "In_Closeness_Distribution")
        elif self.clicked.get() == "Out_Closeness":
            Out_closeness_centrality_values = []
            self.plot_distribution(self.det_out_closeness_one(Out_closeness_centrality_values), 7, "In_Closeness_Distribution")
        elif self.clicked.get() == "Betweenness":
            betweenness_values = []
            self.plot_distribution(self.det_betweenness_one(betweenness_values), 6, "Betweenness_Distribution")
            
        elif self.clicked.get() == "Relative_Likelihood":
            relative_likelihood_list = []
            relative_likelihood = self.det_relative_likelihood()
            for i in range(len(relative_likelihood)):
                relative_likelihood_list.append(relative_likelihood.get(str(i)))
            self.plot_distribution(relative_likelihood_list, 11, 'Relative_Likelihood')
            
        elif self.clicked.get() == "Causal_Contribution":
            Causal_Contribution_list = []
            Causal_Contribution = self.det_causal_contribution()
            for i in range(len(Causal_Contribution)):
                Causal_Contribution_list.append(Causal_Contribution.get(str(i)))
            self.plot_distribution(Causal_Contribution_list, 12, 'Causal_Contribution')
            
    def show_robustness_connected(self):
        if self.clicked.get() == "Degree":
            self.delete_by_degree_connected()
        elif self.clicked.get() == "In_Degree":
            self.delete_by_In_degree_connected()
        elif self.clicked.get() == "Out_Degree":
            self.delete_by_Out_degree_connected()
        elif self.clicked.get() == "Strength":
            self.delete_by_Strength_connected()
        elif self.clicked.get() == "In_Strength":
            self.delete_by_In_Strength_connected()
        elif self.clicked.get() == "Out_Strength":
            self.delete_by_Out_Strength_connected()
        elif self.clicked.get() == "Eigenvector":
            self.delete_by_Eigenvector_connected()
        elif self.clicked.get() == "In_Closeness":
            self.delete_by_Closeness_connected()
        elif self.clicked.get() == "Out_Closeness":
            self.delete_by_Out_Closeness_connected()
        elif self.clicked.get() == "Betweenness":
            self.delete_by_Betweenness_connected()
        elif self.clicked.get() == "Relative_Likelihood":
            self.delete_by_relative_likelihood_connected()
        elif self.clicked.get() == "Causal_Contribution":
            self.delete_by_causal_contribution_connected()
            
    def show_robustness_remaining(self):
        if self.clicked.get() == "Degree":
            self.delete_by_degree_remaining()
        elif self.clicked.get() == "In_Degree":
            self.delete_by_In_degree_remaining()
        elif self.clicked.get() == "Out_Degree":
            self.delete_by_Out_degree_remaining()
        elif self.clicked.get() == "Strength":
            self.delete_by_Strength_remaining()
        elif self.clicked.get() == "In_Strength":
            self.delete_by_In_Strength_remaining()
        elif self.clicked.get() == "Out_Strength":
            self.delete_by_Out_Strength_remaining()
        elif self.clicked.get() == "Eigenvector":
            self.delete_by_Eigenvector_remaining()
        elif self.clicked.get() == "In_Closeness":
            self.delete_by_Closeness_remaining()
        elif self.clicked.get() == "Out_Closeness":
            self.delete_by_Out_Closeness_remaining()
        elif self.clicked.get() == "Betweenness":
            self.delete_by_Betweenness_remaining()
        elif self.clicked.get() == "Relative_Likelihood":
            self.delete_by_relative_likelihood_remaining()
        elif self.clicked.get() == "Causal_Contribution":
            self.delete_by_causal_contribution_remaining() 
            
    def save_matrix(self):
        if self._filename is None:
            filename = filedialog.asksaveasfilename(filetypes=[("Text file", ".txt")])
            if filename:
                self._filename = filename
        if self._filename:
            self._master.title(self._filename)
            np.savetxt(self._filename, self._adjacency_matrix, fmt="%d", delimiter=",")

        a = self._matrix.get_node_ID()
        res = dict((v,k) for k,v in a.items())
        df_IDs = pd.DataFrame.from_dict(res,orient='index',columns=['Description'])
        df_IDs.to_csv(filename + "_lookup.csv")
    
    def quit(self):
        """Execute the program"""
        self._master.destroy()

    def get_dict(self, list1):
        output = dict([(i[0], i[1]) for i in list1])
        return output

    def get_Digraph(self):
        """ Return the directed graph structure from the adjacency matrix"""
        G = nx.DiGraph(directed=True)
        
        print("[{}] started get_Digraph()".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        for i in range(len(self._adjacency_matrix)):
            for j in range(len(self._adjacency_matrix)):
                weight=int(self._adjacency_matrix[i][j])
                if weight>0:
                    color = self.get_color(weight-1)
                    G.add_edge(str(i), str(j), color=color,weight=weight)
        
        print("[{}] finished get_Digraph()".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        return G

    def plot_Digraph_initial(self):
        """ Plot the directed graph structure on the canvas"""
        fig = plt.figure(figsize=(6, 6), dpi=200)

        plt.axis('off')
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0,
                            hspace=0, wspace=0)
        pos = nx.nx_agraph.graphviz_layout(self._digraph_normal)
        colors = nx.get_edge_attributes(self._digraph_normal, 'color').values()
        options = {'font_size': 3, 'font_color': 'white', 'node_color': 'black', 'node_size': 60,
                   'style': 'solid',
                   'width': 0.3
                   }
        nx.draw_networkx(self._digraph_normal, pos, edge_color=colors, arrows=True, arrowsize=2,
                         **options)
        plt.margins(0, 0)
        plt.savefig("initial_Digraph.png", dpi=800, pad_inches=0)
        print("[{}] Created: initial_Digraph.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        for widget in self._frame_one.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self._frame_one)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=None, expand=tk.YES)

    def plot_ColorMap(self, measures, measure_name):
        """ Plot the colormap structure (Degree, In-degree, Out-degree, Betweenness, Closeness) on the canvas"""
        fig = plt.figure(figsize=(6, 6), dpi=200)
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        colors = nx.get_edge_attributes(self._digraph_normal, 'color').values()
        options = {'font_size': 3, 'font_color': 'white', 'node_color': 'black', 'node_size': 50, 'style': 'solid',
                   'width': 0.3}
        nx.draw_networkx(self._digraph_normal, self._pos, edge_color=colors, arrows=True, arrowsize=2, **options)

        cmap = plt.get_cmap('jet', 10)
        cmap.set_under('gray')
        nodes = nx.draw_networkx_nodes(self._digraph_normal, self._pos, node_size=50, cmap=cmap,
                                       node_color=list(measures.values()),
                                       nodelist=measures.keys())
        min = 10000
        max = 0
        for i in measures.values():
            if i > max:
                max = i
            if i < min:
                min = i
        nodes.set_norm(mcolors.SymLogNorm(linthresh=1, linscale=10, vmin=min, vmax=max))
        plt.margins(0, 0)
        plt.title(measure_name)
        cbar = plt.colorbar(nodes, shrink=0.2)
        cbar.ax.tick_params(labelsize=5)
        plt.axis('off')
        plt.savefig(measure_name + ".png", dpi=800, pad_inches=0)
        print("[{}] Created: {}".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S"),measure_name + ".png"))
        for widget in self._frame_one.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self._frame_one)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=None, expand=tk.YES)

    def plot_ColorMap_eigen(self, measures, measure_name):
        """ Plot the colormap structure (Eigenvector) on the canvas"""
        fig = plt.figure(figsize=(6, 6), dpi=200)
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        colors = nx.get_edge_attributes(self._digraph_normal, 'color').values()
        options = {'font_size': 3, 'font_color': 'white', 'node_color': 'black', 'node_size': 50, 'style': 'solid',
                   'width': 0.3}
        nx.draw_networkx(self._digraph_normal, self._pos, edge_color=colors, arrows=True, arrowsize=2, **options)

        cmap = plt.get_cmap('jet', 10)
        cmap.set_under('gray')
        nodes = nx.draw_networkx_nodes(self._digraph_normal, self._pos, node_size=50, cmap=cmap,
                                       node_color=list(measures.values()),
                                       nodelist=measures.keys())
        min = 1
        max = 0
        for i in measures.values():
            if i > max:
                max = i
            if i < min:
                min = i
        nodes.set_norm(mcolors.SymLogNorm(linthresh=1, linscale=1, vmin=0, vmax=0.001))
        plt.margins(0, 0)
        plt.title(measure_name)
        cbar = plt.colorbar(nodes, shrink=0.2)
        cbar.ax.tick_params(labelsize=5)
        plt.axis('off')
        plt.savefig(measure_name + ".png", dpi=800, pad_inches=0)
        print("[{}] Created: {}".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S"),measure_name + ".png"))
        for widget in self._frame_one.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self._frame_one)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=None, expand=tk.YES)

    def openImage(self, fileName):
        f = Image.open(fileName)
        f.show()

    def neighbor_of_nodes(self):
        """(Distionary): Returns node_ID as keys and pointing nodes as values in list structure"""
        nodes = {}
        for i in range(len(self._adjacency_matrix)):
            node_neighbor = []
            for neighbor, value in enumerate(self._adjacency_matrix[i]):
                if value != 0:
                    node_neighbor.append(neighbor)
            if len(node_neighbor) != 0:
                nodes[i] = node_neighbor
        return nodes

    def new(self, saved_list, component, index):
        """ Delete the node inside the node_no from adjacency matrix.

        Parameters:
            saved_list(List): Initial empty list, store pointed nodes need to be recursive to add to connected component.
            component(List): Initial empty list, store final connected nodes as a component.
            index(Int): Index of node in node_neighbor dictionary.
        """
        if len(self._node_neighbor) == 0:
            return
        else:
            saved_list.append(list(self._node_neighbor.keys())[index])
            saved_list.extend(self._node_neighbor[list(self._node_neighbor.keys())[index]])
            saved_list = list(dict.fromkeys(saved_list))
            del self._node_neighbor[list(self._node_neighbor.keys())[index]]
            if len(self._node_neighbor) == 0:
                saved_list = list(dict.fromkeys(saved_list))
                if saved_list not in component:
                    component.append(saved_list)
            else:
                for i in list(self._node_neighbor.keys()):
                    for j in self._node_neighbor[i]:
                        ## Both incident nodes and being pointed nodes are connected component
                        if i in saved_list:
                            saved_list = list(dict.fromkeys(saved_list))
                            self.new(saved_list, component, list(self._node_neighbor.keys()).index(i))
                            break

                        elif j in saved_list:
                            saved_list = list(dict.fromkeys(saved_list))
                            self.new(saved_list, component, list(self._node_neighbor.keys()).index(i))
                            break

                    saved_list = list(dict.fromkeys(saved_list))
                    if saved_list not in component:
                        saved_list = list(dict.fromkeys(saved_list))
                        component.append(saved_list)
                    if len(self._node_neighbor) < 1:
                        break

                saved_list = []
                self.new(saved_list, component, 0)
                
### Robustness of network focusing on number of remaining nodes   
    def delete_by_degree_remaining(self):
        """
        Delete all the nodes by the descending order of value of degree.
        """
        count = -1
        name = ''
        a = self._digraph_normal.degree
        component = []
        while len(a) != 0:
            for i in a:
                if i[1] > count:
                    count = i[1]
                    name = i[0]
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self._number_of_remaining_nodes.append(self._digraph_normal.number_of_nodes())
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            a = self._digraph_normal.degree
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._number_of_remaining_nodes.append(0)
        sub1.plot(a, self._number_of_remaining_nodes)
        y = np.array(self._number_of_remaining_nodes)
        area = int(simps(y, x=np.array(a)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of degree')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Number of Remaining Nodes')
        fig1.savefig('Robustness_Degree_Remaining_Nodes.png')
        print("[{}] Created: Robustness_Degree_Remaining_Nodes.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        workbook = xlsxwriter.Workbook('Robustness_Degree_Remaining_Nodes.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Number of Remaining Nodes")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._number_of_remaining_nodes:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()
        
    def delete_by_Out_degree_remaining(self):
        """ Delete all the nodes by the descending order of value of Out Degree."""
        count = 0
        name = ''
        a = self._digraph_normal.out_degree
        component = []
        while len(a) != 0:
            for i in a:
                if i[1] > count:
                    count = i[1]
                    name = i[0]
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self._number_of_remaining_nodes.append(self._digraph_normal.number_of_nodes())
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = 0
            name = ''
            a = self._digraph_normal.out_degree
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._number_of_remaining_nodes.append(0)
        sub1.plot(a, self._number_of_remaining_nodes)
        y = np.array(self._number_of_remaining_nodes)
        area = int(simps(y, x=np.array(a)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of Out_Degree')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Number of Remaining Nodes')
        fig1.savefig('Robustness_Out_Degree_Remaining_Nodes.png')
        print("[{}] Created: Robustness_Out_Degree_Remaining_Nodes.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_Out_Degree_Remaining_Nodes.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Number_of_Remaining_Nodes")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._number_of_remaining_nodes:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()
        
    def delete_by_In_degree_remaining(self):
        """ Delete all the nodes by the descending order of value of In Degree."""
        count = 0
        name = ''
        a = self._digraph_normal.in_degree
        component = []
        while len(a) != 0:
            for i in a:
                if i[1] > count:
                    count = i[1]
                    name = i[0]
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self._number_of_remaining_nodes.append(self._digraph_normal.number_of_nodes())
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = 0
            name = ''
            a = self._digraph_normal.in_degree
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._number_of_remaining_nodes.append(0)
        sub1.plot(a, self._number_of_remaining_nodes)
        y = np.array(self._number_of_remaining_nodes)
        area = int(simps(y, x=np.array(a)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of In_Degree')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Number of Remaining Nodes')
        fig1.savefig('Robustness_In_Degree_Remaining_Nodes.png')
        print("[{}] Created: Robustness_In_Degree_Remaining_Nodes.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_In_Degree_Remaining_Nodes.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Number_of_Remaining_Nodes")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._number_of_remaining_nodes:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()
        
    def delete_by_Closeness_remaining(self):
        """ Delete all the nodes by the descending order of value of In_Closeness."""
        count = -1
        name = ''
        cc = 0
        aa = []
        a = nx.closeness_centrality(self._digraph_normal, distance="weight")
        component = []
        while len(a) != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self._number_of_remaining_nodes.append(self._digraph_normal.number_of_nodes())
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            a = nx.closeness_centrality(self._digraph_normal, distance="weight")
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._number_of_remaining_nodes.append(0)
        sub1.plot(a, self._number_of_remaining_nodes)
        y = np.array(self._number_of_remaining_nodes)
        area = int(simps(y, x=np.array(a)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of In_Closeness')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Number of Remaining Nodes')
        fig1.savefig('Robustness_In_Closeness_Remaining_Nodes.png')
        print("[{}] Created: Robustness_In_Closeness_Remaining_Nodes.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_In_Closeness_Remaining_Nodes.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Number of Remaining Nodes")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._number_of_remaining_nodes:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()
        
    def delete_by_Out_Closeness_remaining(self):
        """ Delete all the nodes by the descending order of value of Closeness."""
        count = -1
        name = ''
        cc = 0
        aa = []
        a = nx.closeness_centrality(self._digraph_normal.reverse(), distance="weight")
        component = []
        while len(a) != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self._number_of_remaining_nodes.append(self._digraph_normal.number_of_nodes())
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            a = nx.closeness_centrality(self._digraph_normal.reverse(), distance="weight")
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._number_of_remaining_nodes.append(0)
        sub1.plot(a, self._number_of_remaining_nodes)
        y = np.array(self._number_of_remaining_nodes)
        area = int(simps(y, x=np.array(a)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of Out_Closeness')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Number of Remaining Nodes')
        fig1.savefig('Robustness_Out_Closeness_Remaining_Nodes.png')
        print("[{}] Created: Robustness_Out_Closeness_Remaining_Nodes.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_Out_Closeness_Remaining_Nodes.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Number of remaining nodes")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._number_of_remaining_nodes:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()
        
    def delete_by_Eigenvector_remaining(self):
        """ Delete all the nodes by the descending order of value of Eigenvector."""
        count = -1
        name = ''
        b = len(self._digraph_normal)
        a = nx.eigenvector_centrality(self._digraph_normal, tol=1e-03)
        component = []
        while b != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self._number_of_remaining_nodes.append(self._digraph_normal.number_of_nodes())
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            if len(self._digraph_normal) != 0:
                a = nx.eigenvector_centrality(self._digraph_normal, tol=1e-03)
            else:
                break
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._number_of_remaining_nodes.append(0)
        sub1.plot(a, self._number_of_remaining_nodes)
        y = np.array(self._number_of_remaining_nodes)
        area = int(simps(y, x=np.array(a)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of Eigenvector')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Number of Remainig Nodes')
        fig1.savefig('Robustness_Eigenvector_Remaining_Nodes.png')
        print("[{}] Created: Robustness_Eigenvector_Remain.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_Eigenvector_Remaining_Nodes.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Number of Remaining Nodes")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._number_of_remaining_nodes:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()
        
    def delete_by_Betweenness_remaining(self):
        """ Delete all the nodes by the descending order of value of Betweenness."""
        count = -1
        name = ''
        a = nx.betweenness_centrality(self._digraph_normal, normalized=True,weight="weight")
        component = []
        cc = 0
        aa = []
        while len(a) != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self._number_of_remaining_nodes.append(self._digraph_normal.number_of_nodes())
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            cc = 0
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            a = nx.betweenness_centrality(self._digraph_normal, normalized=True,weight="weight")
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._number_of_remaining_nodes.append(0)
        sub1.plot(a, self._number_of_remaining_nodes)
        y = np.array(self._number_of_remaining_nodes)
        area = int(simps(y, x=np.array(a)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of Betweenness')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Number of Remaining Nodes')
        fig1.savefig('Robustness_Betweenness_Remaining_Nodes.png')
        print("[{}] Created: Robustness_Betweenness_Remaining_Nodes.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_Betweenness_Remaining_Nodes.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Number of Remaining Nodes")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._number_of_remaining_nodes:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()
        
    def delete_by_Strength_remaining(self):
        """ Delete all the nodes by the descending order of value of Strength."""
        count = -1
        name = ''
        b = len(self._digraph_normal)
        instrength = self.det_instrength()
        outstrength = self.det_outstrength()
        a = self.det_strength(instrength, outstrength)
        component = []
        while b != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self._number_of_remaining_nodes.append(self._digraph_normal.number_of_nodes())
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            if len(self._digraph_normal) != 0:
                instrength = self.det_instrength()
                outstrength = self.det_outstrength()
                a = self.det_strength(instrength, outstrength)
            else:
                break
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._number_of_remaining_nodes.append(0)
        sub1.plot(a, self._number_of_remaining_nodes)
        y = np.array(self._number_of_remaining_nodes)
        area = int(simps(y, x=np.array(a)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of Strength')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Number of Remaining Nodes')
        fig1.savefig('Robustness_Strength_Remaining_Nodes.png')
        print("[{}] Created: Robustness_Strength_Remaining_Nodes.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_Strength_Remaining_Nodes.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Number of Remaining Nodes")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._number_of_remaining_nodes:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()
        
    def delete_by_In_Strength_remaining(self):
        """ Delete all the nodes by the descending order of value of Instrength."""
        count = -1
        name = ''
        b = len(self._digraph_normal)
        a = self.det_instrength()
        component = []
        while b != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self._number_of_remaining_nodes.append(self._digraph_normal.number_of_nodes())
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            if len(self._digraph_normal) != 0:
                a = self.det_instrength()
            else:
                break
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._number_of_remaining_nodes.append(0)
        sub1.plot(a, self._number_of_remaining_nodes)
        y = np.array(self._number_of_remaining_nodes)
        area = int(simps(y, x=np.array(a)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of In_Strength')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Number of Reamining Nodes')
        fig1.savefig('Robustness_In_Strength_Remaining_Nodes.png')
        print("[{}] Created: Robustness_In_Strength_Remaining_Nodes.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_In_Strength_Remaining_Nodes.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Number of Remaining Nodes")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._number_of_remaining_nodes:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()
        
    def delete_by_Out_Strength_remaining(self):
        """ Delete all the nodes by the descending order of value of OutStrength."""
        count = -1
        name = ''
        b = len(self._digraph_normal)
        a = self.det_outstrength()
        component = []
        while b != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self._number_of_remaining_nodes.append(self._digraph_normal.number_of_nodes())
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            if len(self._digraph_normal) != 0:
                a = self.det_outstrength()
            else:
                break
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._number_of_remaining_nodes.append(0)
        sub1.plot(a, self._number_of_remaining_nodes)
        y = np.array(self._number_of_remaining_nodes)
        area = int(simps(y, x=np.array(a)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of Out_Strength')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Number of Remaining Nodes')
        fig1.savefig('Robustness_Out_Strength_Remaining_Nodes.png')
        print("[{}] Created: Robustness_Out_Strength_Remaining_Nodes.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_Out_Strength_Remaining_Nodes.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Number of Remaining Nodes")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._number_of_remaining_nodes:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()
        
    def delete_by_relative_likelihood_remaining(self):
        """ Delete all the nodes by the descending order of value of relative_likelihood."""
        count = -1
        name = ''
        b = len(self._digraph_normal)
        a = self.det_relative_likelihood()
        component = []
        while b != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self._number_of_remaining_nodes.append(self._digraph_normal.number_of_nodes())
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            if len(self._digraph_normal) != 0:
                a = self.det_relative_likelihood()
            else:
                break
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._number_of_remaining_nodes.append(0)
        sub1.plot(a, self._number_of_remaining_nodes)
        y = np.array(self._number_of_remaining_nodes)
        area = int(simps(y, x=np.array(a)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of relative_likelihood')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Number of Remaining Nodes')
        fig1.savefig('Robustness_relative_likelihood_Remaining_Nodes.png')
        print("[{}] Created: Robustness_relative_likelihood_Remaining_Nodes.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_relative_likelihood_Remaining_Nodes.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Number of Remaining Nodes")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._number_of_remaining_nodes:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()
             
    def delete_by_causal_contribution_remaining(self):
        """ Delete all the nodes by the descending order of value of causal_contribution."""
        count = -1
        name = ''
        b = len(self._digraph_normal)
        a = self.det_causal_contribution()
        component = []
        while b != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self._number_of_remaining_nodes.append(self._digraph_normal.number_of_nodes())
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            if len(self._digraph_normal) != 0:
                a = self.det_causal_contribution()
            else:
                break
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._number_of_remaining_nodes.append(0)
        sub1.plot(a, self._number_of_remaining_nodes)
        y = np.array(self._number_of_remaining_nodes)
        area = int(simps(y, x=np.array(a)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of causal_contribution')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Number of Remaining Nodes')
        fig1.savefig('Robustness_causal_contribution_Remaining_Nodes.png')
        print("[{}] Created: Robustness_causal_contribution_Remaining_Nodes.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_causal_contribution_Remaining_Nodes.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Number of Remaining Nodes")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._number_of_remaining_nodes:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()
     
### Robustness of network focusing on largest connected component
    def delete_by_degree_connected(self):
        """
        Delete all the nodes by the descending order of value of degree.
        """
        count = -1
        name = ''
        a = self._digraph_normal.degree
        component = []
        while len(a) != 0:
            for i in a:
                if i[1] > count:
                    count = i[1]
                    name = i[0]
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self.new([], component, 0)
            max_length = max([(len(x)) for x in component])
            self._largest_connected_component.append(max_length)
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            a = self._digraph_normal.degree
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._largest_connected_component.append(0)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node)+1))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of degree')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_Degree.png')
        print("[{}] Created: Robustness_Degree.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        workbook = xlsxwriter.Workbook('Robustness_Degree_Connected.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Size of Remaining Largest Component")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._largest_connected_component:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()
                    
    def delete_by_In_degree_connected(self):
        """ Delete all the nodes by the descending order of value of In Degree."""
        count = -1
        name = ''
        a = self._digraph_normal.in_degree
        component = []
        while len(a) != 0:
            for i in a:
                if i[1] > count:
                    count = i[1]
                    name = i[0]
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self.new([], component, 0)
            max_length = max([(len(x)) for x in component])
            self._largest_connected_component.append(max_length)
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            a = self._digraph_normal.in_degree
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._largest_connected_component.append(0)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node) + 1))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of In_Degree')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_In_Degree.png')
        print("[{}] Created: Robustness_In_Degree.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))

        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_In_Degree_Connected.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Size of Remaining Largest Component")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._largest_connected_component:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()

    def delete_by_Out_degree_connected(self):
        """ Delete all the nodes by the descending order of value of Out Degree."""
        count = 0
        name = ''
        a = self._digraph_normal.out_degree
        component = []
        while len(a) != 0:
            for i in a:
                if i[1] > count:
                    count = i[1]
                    name = i[0]
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self.new([], component, 0)
            max_length = max([(len(x)) for x in component])
            self._largest_connected_component.append(max_length)
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = 0
            name = ''
            a = self._digraph_normal.out_degree
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._largest_connected_component.append(0)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node) + 1))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of Out_Degree')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_Out_Degree.png')
        print("[{}] Created: Robustness_Out_Degree.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_Out_Degree_Connected.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Size of Remaining Largest Component")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._largest_connected_component:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()

    def delete_by_Closeness_connected(self):
        """ Delete all the nodes by the descending order of value of In_Closeness."""
        count = -1
        name = ''
        cc = 0
        aa = []
        a = nx.closeness_centrality(self._digraph_normal, distance="weight")
        component = []
        while len(a) != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self.new([], component, 0)
            for i in component:
                if len(i) > cc:
                    cc = len(i)
                    aa.append(i)
                    if len(aa) != 1:
                        aa.pop(0)
            cc = 0
            max_length = max([(len(x)) for x in component])
            self._largest_connected_component.append(max_length)
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            a = nx.closeness_centrality(self._digraph_normal, distance="weight")
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._largest_connected_component.append(0)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node)+1))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of In_Closeness')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_In_Closeness.png')
        print("[{}] Created: Robustness_In_Closeness.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_In_Closeness_Connected.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Size of Remaining Largest Component")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._largest_connected_component:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()
        
    def delete_by_Out_Closeness_connected(self):
        """ Delete all the nodes by the descending order of value of Closeness."""
        count = -1
        name = ''
        cc = 0
        aa = []
        a = nx.closeness_centrality(self._digraph_normal.reverse(), distance="weight")
        component = []
        while len(a) != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self.new([], component, 0)
            for i in component:
                if len(i) > cc:
                    cc = len(i)
                    aa.append(i)
                    if len(aa) != 1:
                        aa.pop(0)
            cc = 0
            max_length = max([(len(x)) for x in component])
            self._largest_connected_component.append(max_length)
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            a = nx.closeness_centrality(self._digraph_normal.reverse(), distance="weight")
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._largest_connected_component.append(0)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node)+1))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of Out_Closeness')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_Out_Closeness.png')
        print("[{}] Created: Robustness_Out_Closeness.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_Out_Closeness_Connected.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Size of Remaining Largest Component")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._largest_connected_component:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()

    def delete_by_Eigenvector_connected(self):
        """ Delete all the nodes by the descending order of value of Eigenvector."""
        count = -1
        name = ''
        b = len(self._digraph_normal)
        a = nx.eigenvector_centrality(self._digraph_normal, tol=1e-03)
        component = []
        while b != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self.new([], component, 0)
            max_length = max([(len(x)) for x in component])
            self._largest_connected_component.append(max_length)
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            if len(self._digraph_normal) != 0:
                a = nx.eigenvector_centrality(self._digraph_normal, tol=1e-03)
            else:
                break
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._largest_connected_component.append(0)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node)+1))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of Eigenvector')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_Eigenvector.png')
        print("[{}] Created: Robustness_Eigenvector.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_Eigenvector_Connected.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Size of Remaining Largest Component")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._largest_connected_component:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()
        
    def delete_by_Strength_connected(self):
        """ Delete all the nodes by the descending order of value of Strength."""
        count = -1
        name = ''
        b = len(self._digraph_normal)
        instrength = self.det_instrength()
        outstrength = self.det_outstrength()
        a = self.det_strength(instrength, outstrength)
        component = []
        while b != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self.new([], component, 0)
            max_length = max([(len(x)) for x in component])
            self._largest_connected_component.append(max_length)
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            if len(self._digraph_normal) != 0:
                instrength = self.det_instrength()
                outstrength = self.det_outstrength()
                a = self.det_strength(instrength, outstrength)
            else:
                break
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._largest_connected_component.append(0)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node)+1))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of Strength')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_Strength.png')
        print("[{}] Created: Robustness_Strength.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_Strength_Connected.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Size of Remaining Largest Component")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._largest_connected_component:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()
        
    def delete_by_In_Strength_connected(self):
        """ Delete all the nodes by the descending order of value of Instrength."""
        count = -1
        name = ''
        b = len(self._digraph_normal)
        a = self.det_instrength()
        component = []
        while b != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self.new([], component, 0)
            max_length = max([(len(x)) for x in component])
            self._largest_connected_component.append(max_length)
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            if len(self._digraph_normal) != 0:
                a = self.det_instrength()
            else:
                break
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._largest_connected_component.append(0)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node)+1))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of In_Strength')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_In_Strength.png')
        print("[{}] Created: Robustness_In_Strength.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_In_Strength_Connected.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Size of Remaining Largest Component")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._largest_connected_component:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()
        
    def delete_by_Out_Strength_connected(self):
        """ Delete all the nodes by the descending order of value of OutStrength."""
        count = -1
        name = ''
        b = len(self._digraph_normal)
        a = self.det_outstrength()
        component = []
        while b != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self.new([], component, 0)
            max_length = max([(len(x)) for x in component])
            self._largest_connected_component.append(max_length)
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            if len(self._digraph_normal) != 0:
                a = self.det_outstrength()
            else:
                break
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._largest_connected_component.append(0)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node)+1))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of Out_Strength')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_Out_Strength.png')
        print("[{}] Created: Robustness_Out_Strength.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_Out_Strength_Connected.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Size of Remaining Largest Component")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._largest_connected_component:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()
        
    def delete_by_relative_likelihood_connected(self):
        """ Delete all the nodes by the descending order of value of relative_likelihood."""
        count = -1
        name = ''
        b = len(self._digraph_normal)
        a = self.det_relative_likelihood()
        component = []
        while b != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self.new([], component, 0)
            max_length = max([(len(x)) for x in component])
            self._largest_connected_component.append(max_length)
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            if len(self._digraph_normal) != 0:
                a = self.det_relative_likelihood()
            else:
                break
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._largest_connected_component.append(0)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node)+1))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of relative_likelihood')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_relative_likelihood.png')
        print("[{}] Created: Robustness_relative_likelihood.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_relative_likelihood_Connected.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Size of Remaining Largest Component")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._largest_connected_component:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()
         
    def delete_by_causal_contribution_connected(self):
        """ Delete all the nodes by the descending order of value of causal_contribution."""
        count = -1
        name = ''
        b = len(self._digraph_normal)
        a = self.det_causal_contribution()
        component = []
        while b != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self.new([], component, 0)
            max_length = max([(len(x)) for x in component])
            self._largest_connected_component.append(max_length)
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            if len(self._digraph_normal) != 0:
                a = self.det_causal_contribution()
            else:
                break
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._largest_connected_component.append(0)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node)+1))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of causal_contribution')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_causal_contribution.png')
        print("[{}] Created: Robustness_causal_contribution.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_causal_contribution_Connected.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Size of Remaining Largest Component")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._largest_connected_component:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()

    def delete_by_Betweenness_connected(self):
        """ Delete all the nodes by the descending order of value of Betweenness."""
        count = -1
        name = ''
        a = nx.betweenness_centrality(self._digraph_normal, normalized=True,weight="weight")
        component = []
        cc = 0
        aa = []
        while len(a) != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self.new([], component, 0)
            for i in component:
                if len(i) > cc:
                    cc = len(i)
                    aa.append(i)
                    if len(aa) != 1:
                        aa.pop(0)
            max_length = max([(len(x)) for x in component])
            self._largest_connected_component.append(max_length)
            component = []
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            cc = 0
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            self._node_neighbor = self.neighbor_of_nodes()
            self._digraph_normal = self.get_Digraph()
            count = -1
            name = ''
            a = nx.betweenness_centrality(self._digraph_normal, normalized=True,weight="weight")
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)+1):
            a.append(i)
        self._largest_connected_component.append(0)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node)+1))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of Betweenness')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_Betweenness.png')
        print("[{}] Created: Robustness_Betweenness.png".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        print("area =", area)
        workbook = xlsxwriter.Workbook('Robustness_Betweenness_Connected.xlsx')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_robustness.write("A1", "No. of Nodes")
        worksheet_robustness.write("B1", "Size of Remaining Largest Component")
        row,row2=2,1
        for i in self._deleted_node:
            worksheet_robustness.write(row,0, str(i))
            row+=1
        for j in self._largest_connected_component:
            worksheet_robustness.write(row2,1, str(j))
            row2+=1
        workbook.close()

    def plot_distribution(self, parameter, figure_number, title):
        """
        Construct distribution plots for each input topology properties on nodes.
        Parameters:
        parameter(List): Showing topology metrics on nodes.
        figure_number(Int): Shows the number of figure.
        title(String): Shows the title of each plots.
        """

        plt.figure(figure_number)

        mean = (np.array(parameter).mean())
        sd = np.array(parameter).std()
        skewness = skew(parameter)

        kurtosis_value = pd.Series(parameter).kurtosis()

        fig, (ax1) = plt.subplots(figsize=(8, 6))
        ax1.hist(parameter, density=False, edgecolor='white')
        plt.axvline(mean, color='k', linestyle='dashed', linewidth=1)
        min_ylim, max_ylim = plt.ylim()
        plt.text(mean * 1.1, max_ylim * 0.9, 'Mean: {:.2f}'.format(mean))
        ax1.set_title(
            f'{title}: $\mu={mean:.2f}$, $\sigma={sd:.2f}$, \nskew={skewness:.2f}, Kurtosis={kurtosis_value:.2f} ')

        for rect in ax1.patches:
            height = rect.get_height()
            ax1.annotate(f'{int(height)}', xy=(rect.get_x() + rect.get_width() / 2, height),
                         xytext=(0, 3), textcoords='offset points', ha='center', va='bottom')

        fig.savefig(title)
        print("[{}] Created: {}".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S"),title))

    def det_indegree(self):
        output = []
        print("[{}] Started Calculating Indegree".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        for i in tqdm(range(len(self._adjacency_matrix)), position=0, leave=True):
            ind = self._digraph_normal.in_degree(str(i))
            if type(ind)==int:
                output.append(ind)
            else:
                # ??? Investigate the root cause of this!
                output.append(0)
                print("Warning [{}] setting in degree to zero!".format(i))
            # if i%10==0:
                # print("[{}] Calculating Indegree <{:,d} of {:,d}>".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S"),i,len(self._adjacency_matrix)))
        return output

    def det_outdegree(self):
        print("[{}] Started Calculating Outdegree".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        output = []
        for i in tqdm(range(len(self._adjacency_matrix)), position=0, leave=True):
            outd= self._digraph_normal.out_degree(str(i))
            if type(outd)==int:
                output.append(outd)
            else:
               # ??? Investigate the root cause of this!
               output.append(0)
               print("Warning [{}] setting out degree to zero!".format(i))
            # if i%10==0:
                # print("[{}] Calculating Outdegree <{:,d} of {:,d}>".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S"),i,len(self._adjacency_matrix)))
        return output

    def det_degree(self, indegree, outdegree):
        sum = [indegree, outdegree]
        output = []
        for x, y in zip(*sum):
            output.append(x + y)
        return output
    
    def det_instrength(self):
        output = {}
        for i in range(len(self._adjacency_matrix)):
            total_incoming_weight = 0
            for j in range(len(self._adjacency_matrix)):
                if self._adjacency_matrix[j][i] != 0:
                    total_incoming_weight += round(1/self._adjacency_matrix[j][i], 2)
            if total_incoming_weight != 0:
                output[str(i)] = total_incoming_weight
            elif total_incoming_weight == 0:
                output[str(i)] = 0
        return output

    def det_outstrength(self):
        output = {}
        for i in range(len(self._adjacency_matrix)):
            total_outcoming_weight = 0
            for j in range(len(self._adjacency_matrix)):
                if self._adjacency_matrix[i][j] != 0:
                    total_outcoming_weight += round(1/self._adjacency_matrix[i][j], 2)
            if total_outcoming_weight != 0:
                output[str(i)] = total_outcoming_weight
            elif total_outcoming_weight == 0:
                output[str(i)] = 0
        return output

    def det_strength(self, instrength, outstrength):
        output = {}
        for i in range(len(self._adjacency_matrix)):
            output[str(i)] = round(instrength.get(str(i)) + outstrength.get(str(i)), 2)
        return output
    
    def det_relative_likelihood(self):
        output = {}
        for i in range(len(self._adjacency_matrix)):
            total_incoming_weight = 0
            number_of_incoming_edges = 0
            for j in range(len(self._adjacency_matrix)):
                if self._adjacency_matrix[j][i] != 0:
                    total_incoming_weight += round(1/self._adjacency_matrix[j][i], 2)
                    number_of_incoming_edges += 1
            if total_incoming_weight != 0:
                output[str(i)] = total_incoming_weight * total_incoming_weight/number_of_incoming_edges
            elif total_incoming_weight == 0:
                output[str(i)] = 0
        return output

    def det_causal_contribution(self):
        output = {}
        for i in range(len(self._adjacency_matrix)):
            total_outcoming_weight = 0
            number_of_outcoming_edges = 0
            for j in range(len(self._adjacency_matrix)):
                if self._adjacency_matrix[i][j] != 0:
                    total_outcoming_weight += round(1/self._adjacency_matrix[i][j], 2)
                    number_of_outcoming_edges += 1
            if total_outcoming_weight != 0:
                output[str(i)] = total_outcoming_weight * total_outcoming_weight/number_of_outcoming_edges
            elif total_outcoming_weight == 0:
                output[str(i)] = 0
        return output
    
    def excel_Gather(self):

        """(XLSX file): Excel sheet contains node_ID and Info."""

        workbook = xlsxwriter.Workbook('NODEs.xlsx')
        worksheet_nodes = workbook.add_worksheet('nodes_ID')
        worksheet_matrix = workbook.add_worksheet('Adjacency_Matrix')
        worksheet_colormap = workbook.add_worksheet('Colormaps')
        worksheet_robustness = workbook.add_worksheet('Robustness')
        worksheet_distribution = workbook.add_worksheet('Distribution')
        row = 0
        col = 0
        digraph_normal = self.get_Digraph()
        degree_1 = digraph_normal.degree
        indegree_1 = digraph_normal.in_degree
        outdegree_1 = digraph_normal.out_degree
        instrength_1 = self.det_instrength()
        outstrength_1 = self.det_outstrength()
        strength_1 = self.det_strength(instrength_1, outstrength_1)
        Betweenness_1 = nx.betweenness_centrality(digraph_normal, normalized = True, weight = "weight")
        Eigenvector_1 = nx.eigenvector_centrality(digraph_normal, max_iter=600)
        Closeness_In = nx.closeness_centrality(digraph_normal,distance="weight")
        Closeness_Out = nx.closeness_centrality(digraph_normal.reverse(),distance="weight")
        relative_likelihood = self.det_relative_likelihood()
        causal_contribution = self.det_causal_contribution()
        worksheet_nodes.write(row, col + 2, 'Degree')
        worksheet_nodes.write(row, col + 3, 'In Degree')
        worksheet_nodes.write(row, col + 4, 'Out Degree')
        worksheet_nodes.write(row, col + 5, 'Strength')
        worksheet_nodes.write(row, col + 6, 'In Strength')
        worksheet_nodes.write(row, col + 7, 'Out Strength')
        worksheet_nodes.write(row, col + 8, 'Betweenness_normalized')
        worksheet_nodes.write(row, col + 9, 'Eigenvector_normalized')
        worksheet_nodes.write(row, col + 10, 'In_Closeness_normalized')
        worksheet_nodes.write(row, col + 11, 'Out_Closeness_normalized')
        worksheet_nodes.write(row, col + 12, 'Relative Likelihood')
        worksheet_nodes.write(row, col + 13, 'Causal contribution')

        # Node information
        for i in self._node_ID.keys():
            worksheet_nodes.write(row + 1, col, i)
            worksheet_nodes.write(row + 1, col + 1, self._node_ID[i])
            # Degree
            worksheet_nodes.write(row + 1, col + 2, degree_1(str(self._node_ID[i])))
            # InDegree
            worksheet_nodes.write(row + 1, col + 3, indegree_1(str(self._node_ID[i])))
            # OutDegree
            worksheet_nodes.write(row + 1, col + 4, outdegree_1(str(self._node_ID[i])))
            # Strength
            worksheet_nodes.write(row + 1, col + 5, strength_1.get((str(self._node_ID[i]))))
            # In Strength
            worksheet_nodes.write(row + 1, col + 6, instrength_1.get((str(self._node_ID[i]))))
            # Out Strength
            worksheet_nodes.write(row + 1, col + 7, outstrength_1.get((str(self._node_ID[i]))))
            # Betweenness
            worksheet_nodes.write(row + 1, col + 8,
                                  Betweenness_1.get((str(self._node_ID[i]))))
            # Eigenvector
            worksheet_nodes.write(row + 1, col + 9, Eigenvector_1.get((str(self._node_ID[i]))))
            # In_Closeness
            worksheet_nodes.write(row + 1, col + 10,
                                  Closeness_In.get((str(self._node_ID[i]))))
            # Out_Closeness
            worksheet_nodes.write(row + 1, col + 11,
                                  Closeness_Out.get((str(self._node_ID[i]))))
            # Relative Likelihood
            worksheet_nodes.write(row + 1, col + 12,
                                  relative_likelihood.get((str(self._node_ID[i]))))
            # Causal Contribution
            worksheet_nodes.write(row + 1, col + 13,
                                  causal_contribution.get((str(self._node_ID[i]))))
            
            row += 1

        row1 = 0
        col1 = 1

        #Adjacency_Matrix
        for i in range(len(self._adjacency_matrix)):
            worksheet_matrix.write(row1, col1, i)
            col1 += 1
        row1 = 1
        col1 = 0
        for j in range(len(self._adjacency_matrix)):
            worksheet_matrix.write(row1, col1, j)
            for k in range(len(self._adjacency_matrix)):
                worksheet_matrix.write(row1, col1 + 1, self._adjacency_matrix[j][k])
                col1 += 1
            row1 += 1
            col1 = 0

        # Colormap
        # Initial
        worksheet_colormap.write('A1', 'Initial_Digraph:')
        self.plot_Digraph_initial()
        worksheet_colormap.insert_image('D1', 'initial_Digraph.png')

        # Degree
        worksheet_colormap.write('A30', 'Degree_Colormap:')
        self.plot_ColorMap(self.get_dict(degree_1), 'Degree')
        worksheet_colormap.insert_image('D30', 'Degree.png')

        # InDegree
        worksheet_colormap.write('A60', 'In_Degree_Colormap:')
        self.plot_ColorMap(self.get_dict(indegree_1), 'In_Degree')
        worksheet_colormap.insert_image('D60', 'In_Degree.png')

        # OutDegree
        worksheet_colormap.write('M1', 'Out_Degree_Colormap:')
        self.plot_ColorMap(self.get_dict(outdegree_1), 'Out_Degree')
        worksheet_colormap.insert_image('P1', 'Out_Degree.png')

        # Eigenvector
        worksheet_colormap.write('M30', 'Eigenvector_Colormap:')
        self.plot_ColorMap(Eigenvector_1, 'Eigenvector')
        worksheet_colormap.insert_image('P30', 'Eigenvector.png')

        # Betweenness
        worksheet_colormap.write('M60', 'Betweenness_Colormap:')
        self.plot_ColorMap(Betweenness_1, 'Betweenness')
        worksheet_colormap.insert_image('P60', 'Betweenness.png')

        # In_Closeness
        worksheet_colormap.write('Y1', 'In_Closeness_Colormap:')
        self.plot_ColorMap(Closeness_In, 'In_Closeness')
        worksheet_colormap.insert_image('AA1', 'In_Closeness.png')
        
        # Out_Closeness
        worksheet_colormap.write('Y30', 'Out_Closeness_Colormap:')
        self.plot_ColorMap(Closeness_Out, 'Out_Closeness')
        worksheet_colormap.insert_image('AA30', 'Out_Closeness.png')
        
        # Relative Likelihood
        worksheet_colormap.write('Y60', 'Relative Likelihood_Colormap:')
        self.plot_ColorMap(relative_likelihood, 'Relative_Likelihood')
        worksheet_colormap.insert_image('AA60', 'Relative_Likelihood.png')
        
        # Causal Contribution
        worksheet_colormap.write('AJ1', 'Causal Contribution_Colormap:')
        self.plot_ColorMap(causal_contribution, 'Causal_Contribution')
        worksheet_colormap.insert_image('AN1', 'Causal_Contribution.png')
        
        # Strength
        worksheet_colormap.write('AJ30', 'Strength_Colormap:')
        self.plot_ColorMap(strength_1, 'Strength')
        worksheet_colormap.insert_image('AN30', 'Strength.png')
        
        # In_strength
        worksheet_colormap.write('AJ60', 'In_Strength_Colormap:')
        self.plot_ColorMap(instrength_1, 'In_Strength')
        worksheet_colormap.insert_image('AN60', 'In_Strength.png')
        
        # Out_strength
        worksheet_colormap.write('AJ90', 'Out_Strength_Colormap:')
        self.plot_ColorMap(outstrength_1, 'Out_Strength')
        worksheet_colormap.insert_image('AN90', 'Out_Strength.png')

        '''
        # Robustness
        # Degree
        worksheet_robustness.write('A1', 'Degree_Robustness:')
        self.delete_by_degree_connected()
        worksheet_colormap.insert_image('D1', 'Robustness_Degree.png')

        # Indegree
        worksheet_robustness.write('A30', 'In_Degree_Robustness')
        self.delete_by_In_degree_connected()
        worksheet_colormap.insert_image('D30', 'Robustness_In_Degree.png')

        # Outdegree
        worksheet_robustness.write('A60', 'Out_Degree_Robustness')
        self.delete_by_Out_degree_connected()
        worksheet_colormap.insert_image('D60', 'Robustness_Out_Degree.png')

        # Eigenvector
        worksheet_robustness.write('M1', 'Eigenvector_Robustness')
        self.delete_by_Eigenvector_connected()
        worksheet_colormap.insert_image('P1', 'Robustness_Eigenvector.png')

        # Betweenness
        worksheet_robustness.write('M30', 'Betweenness_Robustness')
        self.delete_by_Betweenness_connected()
        worksheet_colormap.insert_image('P30', 'Robustness_Betweenness.png')

        # Closeness
        worksheet_robustness.write('M60', 'Closeness_Robustness')
        self.delete_by_Closeness_connected()
        worksheet_colormap.insert_image('P60', 'Robustness_Closeness.png')
        '''

        Indegree = self.det_indegree()
        Outdegree = self.det_outdegree()
        Degree = self.det_degree(Indegree, Outdegree)
        betweenness_values = []
        In_closeness_centrality_values = []
        Out_closeness_centrality_values = []
        Eigenvector_Centrality_values = []
        strength_list = []
        instrength_1 = self.det_instrength()
        outstrength_1 = self.det_outstrength()
        instrength_list = []
        outstrength_list = []
        strength_1 = self.det_strength(instrength_1, outstrength_1)
        relative_likelihood_list = []
        relative_likelihood = self.det_relative_likelihood()
        Causal_Contribution_list = []
        Causal_Contribution = self.det_causal_contribution()

        # Distribution
        # Degree
        worksheet_distribution.write('A1', 'Degree_Distribution:')
        self.plot_distribution(Degree, 1, "Degree_Distribution")
        worksheet_distribution.insert_image('D1', 'Degree_Distribution.png')

        # Indegree
        worksheet_distribution.write('A30', 'In_Degree_Distribution')
        self.plot_distribution(Indegree, 2, "In_Degree_Distribution")
        worksheet_distribution.insert_image('D30', 'In_Degree_Distribution.png')

        # Outdegree
        worksheet_distribution.write('A60', 'Out_Degree_Distribution')
        self.plot_distribution(Outdegree, 3, "Out_Degree_Distribution")
        worksheet_distribution.insert_image('D60', 'Out_Degree_Distribution.png')

        # Eigenvector
        worksheet_distribution.write('P1', 'Eigenvector_Distribution')
        self.plot_distribution(self.det_eigenvector_one(Eigenvector_Centrality_values), 4, "Eigenvector_Distribution")
        worksheet_distribution.insert_image('S1', 'Eigenvector_Distribution.png')

        # Betweenness
        worksheet_distribution.write('P30', 'Betweenness_Distribution')
        self.plot_distribution(self.det_betweenness_one(betweenness_values), 5, "Betweenness_Distribution")
        worksheet_distribution.insert_image('S30', 'Betweenness_Distribution.png')

        # In_Closeness
        worksheet_distribution.write('P60', 'In_Closeness_Distribution')
        self.plot_distribution(self.det_in_closeness_one(In_closeness_centrality_values), 6, "In_Closeness_Distribution")
        worksheet_distribution.insert_image('S60', 'In_Closeness_Distribution.png')
        
        # Out_Closeness
        worksheet_distribution.write('P90', 'Out_Closeness_Distribution')
        self.plot_distribution(self.det_out_closeness_one(Out_closeness_centrality_values), 7, "Out_Closeness_Distribution")
        worksheet_distribution.insert_image('S90', 'Out_Closeness_Distribution.png')
        
        # Strength
        worksheet_distribution.write('AE1', 'Strength_Distribution')
        for i in range(len(strength_1)):
            strength_list.append(strength_1.get(str(i)))
        self.plot_distribution(strength_list, 8, "Strength_Distribution")
        worksheet_distribution.insert_image('AH1', 'Strength_Distribution.png')
        # In Strength
        worksheet_distribution.write('AE30', 'In_Strength_Distribution')
        for i in range(len(instrength_1)):
            instrength_list.append(instrength_1.get(str(i)))
        self.plot_distribution(instrength_list, 9, "In_Strength_Distribution")
        worksheet_distribution.insert_image('AH30', 'In_Strength_Distribution.png')
        
        # Out Strength
        worksheet_distribution.write('AE60', 'Out_Strength_Distribution')
        outstrength_1 = self.det_instrength()
        for i in range(len(outstrength_1)):
            outstrength_list.append(outstrength_1.get(str(i)))
        self.plot_distribution(outstrength_list, 10, "Out_Strength_Distribution")
        worksheet_distribution.insert_image('AH60', 'Out_Strength_Distribution.png')
        
        # Relative likelihood
        worksheet_distribution.write('AE90', 'Relative_Likelihood_Distribution')
        for i in range(len(relative_likelihood)):
            relative_likelihood_list.append(relative_likelihood.get(str(i)))
        self.plot_distribution(relative_likelihood_list, 11, 'Relative_Likelihood_Distribution')
        worksheet_distribution.insert_image('AH90', 'Relative_Likelihood_Distribution.png')
        # Causal Contribution
        worksheet_distribution.write('AE120', 'Caucal_Contribution_Distribution')
        for i in range(len(Causal_Contribution)):
            Causal_Contribution_list.append(Causal_Contribution.get(str(i)))
        self.plot_distribution(Causal_Contribution_list, 12, 'Causal_Contribution_Distribution')
        worksheet_distribution.insert_image('AH120', 'Causal_Contribution_Distribution.png')

        workbook.close()
        
    def add_button(self):
        """Add button on canvas and bind the clicks on a button to the left clicks."""

        buttonGatherExcel = tk.Button(self._frame_two, text="Results", width=100, activebackground="#33B5E5")
        buttonGatherExcel.bind("<Button-1>", lambda evt: self.excel_Gather())
        buttonGatherExcel.pack()


        buttonInitial = tk.Button(self._frame_two, text="Initial_Digraph", width=100, activebackground="#33B5E5")
        buttonInitial.bind("<Button-1>", lambda evt: self.plot_Digraph_initial())
        buttonInitial.pack()

    def det_betweenness_one(self, betweenness_values):
        for k in range(len(nx.betweenness_centrality(self._digraph_normal,normalized=True,weight="weight"))):
            betweenness_values.append(nx.betweenness_centrality(self._digraph_normal).get(str(k)))
        return betweenness_values

    def det_eigenvector_one(self, Eigenvector_Centrality_values):
        for n in range(len(nx.eigenvector_centrality(self._digraph_normal, tol=1e-03, max_iter=600))):
            Eigenvector_Centrality_values.append(
                nx.eigenvector_centrality(self._digraph_normal, tol=1e-03, max_iter=600).get(str(n)))
        return Eigenvector_Centrality_values

    def det_in_closeness_one(self, in_closeness_centrality_values):
        for m in range(len(nx.closeness_centrality(self._digraph_normal))):
            in_closeness_centrality_values.append(nx.closeness_centrality(self._digraph_normal,distance="weight").get(str(m)))
        return in_closeness_centrality_values
    
    def det_out_closeness_one(self, out_closeness_centrality_values):
        for m in range(len(nx.closeness_centrality(self._digraph_normal.reverse()))):
            out_closeness_centrality_values.append(nx.closeness_centrality(self._digraph_normal.reverse(),distance="weight").get(str(m)))
        return out_closeness_centrality_values

    def entryValueRemove(self):
        """Get the type-in texts (nodes need to be eliminated) and store in a list."""
        aa = self._entry.get().split(',')
        for i in aa:
            self._delete_node.append(i)
        self._matrix.deleteNode(self._delete_node)
        self._adjacency_matrix = self._matrix.adjacency_matrix()
        self._digraph_normal = self.get_Digraph()


if __name__ == "__main__":
    ##plot initial digraph
    root = tk.Tk()
    root.geometry("1600x1600")
    digraphPlot(root)
    root.update()
    print("[{}] finished root update()".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
    root.mainloop()
    print("[{}] finished root mainloop()".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
