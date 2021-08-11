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
        if 'AND' not in node and 'OR' not in node:
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
        if 'OR' in node:
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
        if 'AND' in node and 'OR' not in node:
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

    def splitID(self, node, bracketOR, bracketAND):
        """ Split input node string and number them.

        Parameters:
            node (String): Excel block elements contains node element (Usually contains more than one node element)
            bracketOR(Int): Initial set to zero.
            bracketAND(Int): Initial set to zero.
        """
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
                    self.splitID(i, bracketOR + 1, bracketAND)
            elif bracketOR == 1:
                nodesDeviation = node.split(' OR ')
                for j in nodesDeviation:
                    self.splitID(j, bracketOR, bracketAND)
        if 'AND' in node and 'OR' not in node:
            if bracketAND == 0:
                ## split AND outside brackets
                a = re.split(r' AND \s*(?![^()]*\))', node)
                if len(a) == 1:
                    self.splitID(str(a), bracketOR, bracketAND + 1)
                else:
                    for i in a:
                        self.splitID(i, bracketOR, bracketAND + 1)
            elif bracketAND == 1:
                nodesDeviation = node.split(' AND ')
                for j in nodesDeviation:
                    self.splitID(j, bracketOR, bracketAND)

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
            if row[name[0]] != 'None':
                self.splitID(row[name[0]].rstrip(), 0, 0)
            if row[name[1]] != 'None':
                self.splitID(row[name[1]].rstrip(), 0, 0)
            if row[name[2]] != 'None':
                self.splitID(row[name[2]].rstrip(), 0, 0)
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
        self._matrix = Matrix(self._excel_name, self._node_ID, self._node_weight)
        self._adjacency_matrix = self._matrix.adjacency_matrix()
        self._node_ID = self._matrix.get_node_ID()
        self._digarph_normal = self.get_Digraph()
        self._pos = nx.nx_agraph.graphviz_layout(self._digarph_normal)
        self.add_menu()
        self._frame_one = tk.Frame(self._master, bg='grey', width=2600, height=1800)
        self._frame_one.pack(side=tk.LEFT, expand=1, anchor=tk.W)
        self.plot_Digraph_initial()
        self._frame_two = tk.Frame(self._master, bg='grey')
        self._frame_two.pack()
        self.add_button()
        self._entry = tk.Entry(self._frame_two, font=60, relief='flat', width=50, bg="#33B5E5")
        self._entry.pack()
        self._entry.focus_set()
        self._buttonEntry = tk.Button(self._frame_two, text="Remove", width=50)
        self._buttonEntry.bind("<Button-1>", lambda evt: self.entryValueRemove())
        self._buttonEntry.pack()
        self._largest_component = []
        self._deleted_node = []
        self._node_neighbor = self.neighbor_of_nodes()
        self._largest_connected_component = []

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
        self._filename = filedialog.askopenfilename()
        # If file exists
        if self._filename:
            self._master.title(self._filename)
            self._excel_name = self._filename
            return self._filename

    def re_excel(self):
        """Select another excel file under same direction with this file
           Create Matrix, Redraw the frame and canvas.
        """
        filename = filedialog.askopenfilename()
        self._frame_one.destroy()
        self._frame_two.destroy()
        self._matrix = Matrix(filename, self._node_ID, self._node_weight)
        self._adjacency_matrix = self._matrix.adjacency_matrix()
        self._digarph_normal = self.get_Digraph()
        self._pos = nx.nx_agraph.graphviz_layout(self._digarph_normal)
        self._frame_one = tk.Frame(self._master, bg='grey', width=2600, height=1800)
        self._frame_one.pack(side=tk.LEFT, expand=1, anchor=tk.W)
        self.plot_Digraph_initial()
        self._frame_two = tk.Frame(self._master, bg='grey')
        self._frame_two.pack()
        self.add_button()
        self._entry = tk.Entry(self._frame_two, font=60, relief='flat', width=50, bg="#33B5E5")
        self._entry.pack()
        self._entry.focus_set()
        self._buttonEntry = tk.Button(self._frame_two, text="Remove", width=50)
        self._buttonEntry.bind("<Button-1>", lambda evt: self.entryValueRemove())
        self._buttonEntry.pack()
        self._largest_component = []
        self._deleted_node = []
        self._largest_connected_component = []

    def save_matrix(self):
        if self._filename is None:
            filename = filedialog.asksaveasfilename()
            if filename:
                self._filename = filename
        if self._filename:
            self._master.title(self._filename)
            np.savetxt(self._filename, self._adjacency_matrix, fmt="%d", delimiter=",")

    def quit(self):
        """Execute the program"""
        self._master.destroy()

    def get_dict(self, list1):
        output = dict([(i[0], i[1]) for i in list1])
        return output

    def get_Digraph(self):
        """ Return the directed graph structure from the adjacency matrix"""
        G = nx.DiGraph(directed=True)
        a = []
        for i in range(len(self._adjacency_matrix)):
            a.append(str(i))
        for i in range(len(self._adjacency_matrix)):
            for j in range(len(self._adjacency_matrix)):
                if self._adjacency_matrix[i][j] == 1:
                    G.add_edge(a[i], a[j], color='red', weight=int(self._adjacency_matrix[i][j]))
                elif self._adjacency_matrix[i][j] == 2:
                    G.add_edge(a[i], a[j], color='blue', weight=int(self._adjacency_matrix[i][j]))
                elif self._adjacency_matrix[i][j] == 3:
                    G.add_edge(a[i], a[j], color='green', weight=int(self._adjacency_matrix[i][j]))
                elif self._adjacency_matrix[i][j] == 4:
                    G.add_edge(a[i], a[j], color='yellow', weight=int(self._adjacency_matrix[i][j]))
                elif self._adjacency_matrix[i][j] == 5:
                    G.add_edge(a[i], a[j], color='black', weight=int(self._adjacency_matrix[i][j]))
                elif self._adjacency_matrix[i][j] == 6:
                    G.add_edge(a[i], a[j], color='purple', weight=int(self._adjacency_matrix[i][j]))
                elif self._adjacency_matrix[i][j] > 6:
                    G.add_edge(a[i], a[j], color='grey', weight=int(self._adjacency_matrix[i][j]))
        return G

    def plot_Digraph_initial(self):
        """ Plot the directed graph structure on the canvas"""
        fig = plt.figure(figsize=(6, 6), dpi=200)

        plt.axis('off')
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0,
                            hspace=0, wspace=0)
        self._digarph_normal = self.get_Digraph()
        pos = nx.nx_agraph.graphviz_layout(self._digarph_normal)
        colors = nx.get_edge_attributes(self._digarph_normal, 'color').values()
        options = {'font_size': 3, 'font_color': 'white', 'node_color': 'black', 'node_size': 60,
                   'style': 'solid',
                   'width': 0.3
                   }
        nx.draw_networkx(self._digarph_normal, pos, edge_color=colors, arrows=True, arrowsize=2,
                         **options)
        plt.margins(0, 0)
        plt.savefig("initial_Digraph.png", dpi=800, pad_inches=0)
        for widget in self._frame_one.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self._frame_one)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=None, expand=tk.YES)

    def plot_ColorMap(self, measures, measure_name):
        """ Plot the colormap structure (Degree, In-degree, Out-degree, Betweenness, Closeness) on the canvas"""
        fig = plt.figure(figsize=(6, 6), dpi=200)
        self._digarph_normal = self.get_Digraph()
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        colors = nx.get_edge_attributes(self._digarph_normal, 'color').values()
        options = {'font_size': 3, 'font_color': 'white', 'node_color': 'black', 'node_size': 50, 'style': 'solid',
                   'width': 0.3}
        nx.draw_networkx(self._digarph_normal, self._pos, edge_color=colors, arrows=True, arrowsize=2, **options)

        cmap = plt.get_cmap('jet', 10)
        cmap.set_under('gray')
        nodes = nx.draw_networkx_nodes(self._digarph_normal, self._pos, node_size=50, cmap=cmap,
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
        for widget in self._frame_one.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self._frame_one)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=None, expand=tk.YES)

    def plot_ColorMap_eigen(self, measures, measure_name):
        """ Plot the colormap structure (Eigenvector) on the canvas"""
        fig = plt.figure(figsize=(6, 6), dpi=200)
        self._digarph_normal = self.get_Digraph()
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        colors = nx.get_edge_attributes(self._digarph_normal, 'color').values()
        options = {'font_size': 3, 'font_color': 'white', 'node_color': 'black', 'node_size': 50, 'style': 'solid',
                   'width': 0.3}
        nx.draw_networkx(self._digarph_normal, self._pos, edge_color=colors, arrows=True, arrowsize=2, **options)

        cmap = plt.get_cmap('jet', 10)
        cmap.set_under('gray')
        nodes = nx.draw_networkx_nodes(self._digarph_normal, self._pos, node_size=50, cmap=cmap,
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

    def delete_by_degree_connected(self):
        """
        Delete all the nodes by the descending order of value of degree.
        """
        count = -1
        name = ''
        a = self.get_Digraph().degree
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
            count = -1
            name = ''
            a = self.get_Digraph().degree
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)):
            a.append(i)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of degree')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_Degree.png')

    def delete_by_In_degree_connected(self):
        """ Delete all the nodes by the descending order of value of In Degree."""
        count = -1
        name = ''
        a = self.get_Digraph().in_degree
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

            count = -1
            name = ''
            a = self.get_Digraph().in_degree
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)):
            a.append(i)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of In_Degree')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_In_Degree.png')
        print("area =", area)

    def delete_by_Out_degree_connected(self):
        """ Delete all the nodes by the descending order of value of Out Degree."""
        count = 0
        name = ''
        a = self.get_Digraph().out_degree
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

            count = 0
            name = ''
            a = self.get_Digraph().out_degree
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)):
            a.append(i)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of Out_Degree')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_Out_Degree.png')
        print("area =", area)

    def delete_by_Closeness_connected(self):
        """ Delete all the nodes by the descending order of value of Closeness."""
        count = -1
        name = ''
        cc = 0
        aa = []
        a = nx.closeness_centrality(self.get_Digraph())
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

            count = -1
            name = ''
            a = nx.closeness_centrality(self.get_Digraph())
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)):
            a.append(i)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of Closeness')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_Closeness.png')
        print("area =", area)

    def delete_by_Eigenvector_connected(self):
        """ Delete all the nodes by the descending order of value of Eigenvector."""
        count = -1
        name = ''
        b = len(self.get_Digraph())
        a = nx.eigenvector_centrality(self.get_Digraph(), tol=1e-03)
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

            count = -1
            name = ''
            if len(self.get_Digraph()) != 0:
                a = nx.eigenvector_centrality(self.get_Digraph(), tol=1e-03)
            else:
                break
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)):
            a.append(i)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of Eigenvector')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_Eigenvector.png')
        print("area =", area)

    def delete_by_Betweenness_connected(self):
        """ Delete all the nodes by the descending order of value of Betweenness."""
        count = -1
        name = ''
        a = nx.betweenness_centrality(self.get_Digraph())
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

            count = -1
            name = ''
            a = nx.betweenness_centrality(self.get_Digraph())
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)):
            a.append(i)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of Betweenness')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_Betweenness.png')
        print("area =", area)

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

    def det_indegree(self):
        output = []
        for i in range(len(self._adjacency_matrix)):
            output.append(self.get_Digraph().in_degree(str(i)))
        return output

    def det_outdegree(self):
        output = []
        for i in range(len(self._adjacency_matrix)):
            output.append(self.get_Digraph().out_degree(str(i)))
        return output

    def det_degree(self, indegree, outdegree):
        sum = [indegree, outdegree]
        output = []
        for x, y in zip(*sum):
            output.append(x + y)
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
        degree_1 = self._digarph_normal.degree
        indegree_1 = self._digarph_normal.in_degree
        outdegree_1 = self._digarph_normal.out_degree
        Betweenness_1 = nx.betweenness_centrality(self.get_Digraph())
        Eigenvector_1 = nx.eigenvector_centrality(self.get_Digraph(), max_iter=600)
        Closeness_1 = nx.closeness_centrality(self.get_Digraph())
        worksheet_nodes.write(row, col + 2, 'Degree')
        worksheet_nodes.write(row, col + 3, 'In Degree')
        worksheet_nodes.write(row, col + 4, 'Out Degree')
        worksheet_nodes.write(row, col + 5, 'Betweenness')
        worksheet_nodes.write(row, col + 6, 'Eigenvector')
        worksheet_nodes.write(row, col + 7, 'Closeness')

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
            # Betweenness
            worksheet_nodes.write(row + 1, col + 5,
                                  Betweenness_1.get((str(self._node_ID[i]))))
            # Eigenvector
            worksheet_nodes.write(row + 1, col + 6, Eigenvector_1.get((str(self._node_ID[i]))))
            # Closeness
            worksheet_nodes.write(row + 1, col + 7,
                                  Closeness_1.get((str(self._node_ID[i]))))
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
                worksheet_matrix.write(row1, col1 + 1, self._adjacency_matrix[k][j])
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
        worksheet_colormap.insert_image('D60', 'Degree.png')

        # OutDegree
        worksheet_colormap.write('M1', 'Out_Degree_Colormap:')
        self.plot_ColorMap(self.get_dict(outdegree_1), 'Out_Degree')
        worksheet_colormap.insert_image('P1', 'Degree.png')

        # Eigenvector
        worksheet_colormap.write('M30', 'Eigenvector_Colormap:')
        self.plot_ColorMap(Eigenvector_1, 'Eigenvector')
        worksheet_colormap.insert_image('P30', 'Eigenvector.png')

        # Betweenness
        worksheet_colormap.write('M60', 'Betweenness_Colormap:')
        self.plot_ColorMap(Betweenness_1, 'Betweenness')
        worksheet_colormap.insert_image('P60', 'Betweenness.png')

        # Closeness
        worksheet_colormap.write('Y1', 'Closeness_Colormap:')
        self.plot_ColorMap(Closeness_1, 'Closeness')
        worksheet_colormap.insert_image('AA1', 'Closeness.png')

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
        closeness_centrality_values = []
        Eigenvector_Centrality_values = []

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

        # Closeness
        worksheet_distribution.write('P60', 'Closeness_Distribution')
        self.plot_distribution(self.det_closeness_one(closeness_centrality_values), 6, "Closeness_Distribution")
        worksheet_distribution.insert_image('S60', 'Closeness_Distribution.png')

        workbook.close()


    def add_button(self):
        """Add button on canvas and bind the clicks on a button to the left clicks."""

        buttonGatherExcel = tk.Button(self._frame_two, text="Results", width=50, activebackground="#33B5E5")
        buttonGatherExcel.bind("<Button-1>", lambda evt: self.excel_Gather())
        buttonGatherExcel.pack()


        buttonInitial = tk.Button(self._frame_two, text="Initial_Digraph", width=50, activebackground="#33B5E5")
        buttonInitial.bind("<Button-1>", lambda evt: self.plot_Digraph_initial())
        buttonInitial.pack()

        buttonDegree = tk.Button(self._frame_two, text="Degree", width=50, activebackground="#33B5E5")
        buttonDegree.bind("<Button-1>",
                          lambda evt: self.plot_ColorMap(self.get_dict(self.get_Digraph().degree()), 'Degree'))
        buttonDegree.pack()

        buttonInDegree = tk.Button(self._frame_two, text="InDegree", width=50, activebackground="#33B5E5")
        buttonInDegree.bind("<Button-1>",
                            lambda evt: self.plot_ColorMap(self.get_dict(self.get_Digraph().in_degree()), 'InDegree'))
        buttonInDegree.pack()

        buttonOutDegree = tk.Button(self._frame_two, text="OutDegree", width=50, activebackground="#33B5E5")
        buttonOutDegree.bind("<Button-1>",
                             lambda evt: self.plot_ColorMap(self.get_dict(self.get_Digraph().out_degree()),
                                                            'OutDegree'))
        buttonOutDegree.pack()

        buttonCloseness = tk.Button(self._frame_two, text="Closeness", width=50, activebackground="#33B5E5")
        buttonCloseness.bind("<Button-1>",
                             lambda evt: self.plot_ColorMap(nx.closeness_centrality(self.get_Digraph()), 'Closeness'))
        buttonCloseness.pack()

        buttonEigenvector = tk.Button(self._frame_two, text="Eigenvector", width=50, activebackground="#33B5E5")
        buttonEigenvector.bind("<Button-1>",
                               lambda evt: self.plot_ColorMap_eigen(
                                   nx.eigenvector_centrality(self.get_Digraph(), max_iter=600), 'Eigenvector'))
        buttonEigenvector.pack()

        buttonBetweenness = tk.Button(self._frame_two, text="Betweenness", width=50, activebackground="#33B5E5")
        buttonBetweenness.bind("<Button-1>",
                               lambda evt: self.plot_ColorMap(nx.betweenness_centrality(self.get_Digraph()),
                                                              'Betweenness'))
        buttonBetweenness.pack()

        buttonInitialHQ = tk.Button(self._frame_two, text="Initial_Digraph_HQ", width=50, activebackground="#33B5E5")
        buttonInitialHQ.bind("<Button-1>", lambda evt: self.openImage('initial_Digraph.png'))
        buttonInitialHQ.pack()

        buttonDegreeHQ = tk.Button(self._frame_two, text="Degree_HQ", width=50, activebackground="#33B5E5")
        buttonDegreeHQ.bind("<Button-1>", lambda evt: self.openImage('Degree.png'))
        buttonDegreeHQ.pack()

        buttonInDegreeHQ = tk.Button(self._frame_two, text="InDegree_HQ", width=50, activebackground="#33B5E5")
        buttonInDegreeHQ.bind("<Button-1>", lambda evt: self.openImage('InDegree.png'))
        buttonInDegreeHQ.pack()

        buttonOutDegreeHQ = tk.Button(self._frame_two, text="OutDegree_HQ", width=50, activebackground="#33B5E5")
        buttonOutDegreeHQ.bind("<Button-1>", lambda evt: self.openImage('OutDegree.png'))
        buttonOutDegreeHQ.pack()

        buttonClosenessHQ = tk.Button(self._frame_two, text="Closeness_HQ", width=50, activebackground="#33B5E5")
        buttonClosenessHQ.bind("<Button-1>", lambda evt: self.openImage('Closeness.png'))
        buttonClosenessHQ.pack()

        buttonEigenvectorHQ = tk.Button(self._frame_two, text="Eigenvector_HQ", width=50, activebackground="#33B5E5")
        buttonEigenvectorHQ.bind("<Button-1>", lambda evt: self.openImage('Eigenvector.png'))
        buttonEigenvectorHQ.pack()

        buttonBetweennessHQ = tk.Button(self._frame_two, text="Betweenness_HQ", width=50, activebackground="#33B5E5")
        buttonBetweennessHQ.bind("<Button-1>", lambda evt: self.openImage('Betweenness.png'))
        buttonBetweennessHQ.pack()

        PlotDegree_Robustness = tk.Button(self._frame_two, text="Robustness_Degree", width=50,
                                          activebackground="#33B5E5")
        PlotDegree_Robustness.bind("<Button-1>", lambda evt: self.delete_by_degree_connected())
        PlotDegree_Robustness.pack()

        PlotDegree_Robustness = tk.Button(self._frame_two, text="Robustness_In_Degree", width=50,
                                          activebackground="#33B5E5")
        PlotDegree_Robustness.bind("<Button-1>", lambda evt: self.delete_by_In_degree_connected())
        PlotDegree_Robustness.pack()

        PlotDegree_Robustness = tk.Button(self._frame_two, text="Robustness_Out_Degree", width=50,
                                          activebackground="#33B5E5")
        PlotDegree_Robustness.bind("<Button-1>", lambda evt: self.delete_by_Out_degree_connected())
        PlotDegree_Robustness.pack()

        PlotDegree_Robustness = tk.Button(self._frame_two, text="Robustness_Closeness", width=50,
                                          activebackground="#33B5E5")
        PlotDegree_Robustness.bind("<Button-1>", lambda evt: self.delete_by_Closeness_connected())
        PlotDegree_Robustness.pack()

        PlotDegree_Robustness = tk.Button(self._frame_two, text="Robustness_Eigenvector", width=50,
                                          activebackground="#33B5E5")
        PlotDegree_Robustness.bind("<Button-1>", lambda evt: self.delete_by_Eigenvector_connected())
        PlotDegree_Robustness.pack()

        PlotDegree_Robustness = tk.Button(self._frame_two, text="Robustness_Betweenness", width=50,
                                          activebackground="#33B5E5")
        PlotDegree_Robustness.bind("<Button-1>", lambda evt: self.delete_by_Betweenness_connected())
        PlotDegree_Robustness.pack()

        Indegree = self.det_indegree()
        Outdegree = self.det_outdegree()
        Degree = self.det_degree(Indegree, Outdegree)
        Degree_Distribution = tk.Button(self._frame_two, text="Degree_Distribution", width=50,
                                        activebackground="#33B5E5")
        Degree_Distribution.bind("<Button-1>", lambda evt: self.plot_distribution(Degree, 1, "Degree_Distribution"))
        Degree_Distribution.pack()

        In_Degree_Distribution = tk.Button(self._frame_two, text="Indegree_Distribution", width=50,
                                           activebackground="#33B5E5")
        In_Degree_Distribution.bind("<Button-1>", lambda evt: self.plot_distribution(Indegree, 2,
                                                                                     "In_Degree_Distribution"))
        In_Degree_Distribution.pack()

        Out_Degree_Distribution = tk.Button(self._frame_two, text="Outdegree_Distribution", width=50,
                                            activebackground="#33B5E5")
        Out_Degree_Distribution.bind("<Button-1>", lambda evt: self.plot_distribution(Outdegree, 3,
                                                                                      "Out_Degree_Distribution"))
        Out_Degree_Distribution.pack()

        betweenness_values = []
        closeness_centrality_values = []
        Eigenvector_Centrality_values = []

        closeness_centrality_Distribution = tk.Button(self._frame_two, text="Closeness_Distribution", width=50,
                                                      activebackground="#33B5E5")
        closeness_centrality_Distribution.bind("<Button-1>", lambda evt: self.plot_distribution(
            self.det_closeness_one(closeness_centrality_values), 4, "Closeness_Distribution"))
        closeness_centrality_Distribution.pack()

        Eigenvector_Distribution = tk.Button(self._frame_two, text="Eigenvector_Distribution", width=50,
                                             activebackground="#33B5E5")
        Eigenvector_Distribution.bind("<Button-1>", lambda evt: self.plot_distribution(
            self.det_eigenvector_one(Eigenvector_Centrality_values), 5, "Eigenvector_Distribution"))
        Eigenvector_Distribution.pack()

        Betweenness_Distribution = tk.Button(self._frame_two, text="Betweenness_Distribution", width=50,
                                             activebackground="#33B5E5")
        Betweenness_Distribution.bind("<Button-1>",
                                      lambda evt: self.plot_distribution(self.det_betweenness_one(betweenness_values),
                                                                         6, "Betweenness_Distribution"))
        Betweenness_Distribution.pack()

    def det_betweenness_one(self, betweenness_values):
        for k in range(len(nx.betweenness_centrality(self.get_Digraph()))):
            betweenness_values.append(nx.betweenness_centrality(self.get_Digraph()).get(str(k)))
        return betweenness_values

    def det_eigenvector_one(self, Eigenvector_Centrality_values):
        for n in range(len(nx.eigenvector_centrality(self.get_Digraph(), tol=1e-03, max_iter=600))):
            Eigenvector_Centrality_values.append(
                nx.eigenvector_centrality(self.get_Digraph(), tol=1e-03, max_iter=600).get(str(n)))
        return Eigenvector_Centrality_values

    def det_closeness_one(self, closeness_centrality_values):
        for m in range(len(nx.closeness_centrality(self.get_Digraph()))):
            closeness_centrality_values.append(nx.closeness_centrality(self.get_Digraph()).get(str(m)))
        return closeness_centrality_values

    def entryValueRemove(self):
        """Get the type-in texts (nodes need to be eliminated) and store in a list."""
        aa = self._entry.get().split(',')
        for i in aa:
            self._delete_node.append(i)
        self._matrix.deleteNode(self._delete_node)
        self._adjacency_matrix = self._matrix.adjacency_matrix()


if __name__ == "__main__":
    ##plot initial digraph
    root = tk.Tk()
    root.geometry("1600x1600")
    digraphPlot(root)
    root.update()
    root.mainloop()
