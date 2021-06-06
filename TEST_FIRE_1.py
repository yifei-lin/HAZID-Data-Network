from tkinter import filedialog, messagebox

import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from PIL import ImageTk, Image
from scipy.integrate import simps
from scipy.stats import skew
import xlsxwriter
import re
import tkinter as tk
import matplotlib
from numpy import trapz

matplotlib.use('TkAgg')
import numpy as np
import cv2

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from matplotlib.widgets import Button


class Matrix():
    def __init__(self, excel_name, node_weight: dict, node_ID: dict):
        self._excel_name = excel_name
        self._node_weight = node_weight
        self._node_ID = node_ID
        self._df = self.read_sheet(self._excel_name)
        self._gather_list = []
        self._adjacency_matrix = []
        self.gcm()

    def read_sheet(self, file_name, skiprows=0):
        df = pd.read_excel(file_name, skiprows=skiprows)
        return df

    def checkSame(self, nodeName, dictionaryName):
        for i in dictionaryName.keys():
            if nodeName.lower() == i.lower():
                return True
        return False

    def splitWeight(self, nodeWeight, node, weight, bracketOR, bracketAND):
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
                a = re.split(r' OR \s*(?![^()]*\))', node)
                for i in a:
                    self.splitWeight(nodeWeight, i, weight, bracketOR + 1, bracketAND)
            elif bracketOR > 0:
                if '(' not in node:
                    nodesDeviation = node.split(' OR ')
                    for j in nodesDeviation:
                        self.splitWeight(nodeWeight, j, weight, bracketOR, bracketAND)
                else:
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
                a = re.split(r' OR \s*(?![^()]*\))', node)
                for i in a:
                    self.splitID(i, bracketOR + 1, bracketAND)
            elif bracketOR == 1:
                nodesDeviation = node.split(' OR ')
                for j in nodesDeviation:
                    self.splitID(j, bracketOR, bracketAND)
        if 'AND' in node and 'OR' not in node:
            if bracketAND == 0:
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
                a = re.split(r' OR \s*(?![^()]*\))', node)
                for i in a:
                    self.splitIDD(node_IDD, i, bracketOR + 1, bracketAND)
            elif bracketOR == 1:
                nodesDeviation = node.split(' OR ')
                for j in nodesDeviation:
                    self.splitIDD(node_IDD, j, bracketOR, bracketAND)
        if 'AND' in node and 'OR' not in node:
            if bracketAND == 0:
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
            a = re.split(r' OR \s*(?![^()]*\))', causeNode)
            if len(a) == 1:
                for x in a:
                    if 'OR' in x:
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
        gather_list_two = self._gather_list.copy()
        if len(node_no) == 0:
            self._gather_list = gather_list_two
        else:
            for j in range(len(self._adjacency_matrix)):
                self._adjacency_matrix[j][int(node_no[0])] = 0
            for mid_list in self._gather_list:
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
        adjacency_matrix = np.zeros((len(self._node_ID), len(self._node_ID)))
        for index, row in df.iterrows():
            node_Weight1 = {}
            node_IDD1 = {}
            list_cus = []
            ##Get node weight
            self.splitWeight(node_Weight1, row[name[1]].rstrip(), 1, 0, 0)
            print(node_Weight1)
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


class Handle():


    def __init__(self, master, excel_name="Book99999.xlsx", node_weight={}, node_ID={}):

        self._master = master

        self._excel_name = excel_name
        self._node_weight = node_weight
        self._node_ID = node_ID

        self._matrix = Matrix(self._excel_name, self._node_ID, self._node_weight)
        self._digraphPlot = digraphPlot(self._master, self._matrix)
        self._digraphPlot.pack(fill=tk.BOTH, expand=tk.YES)

        self._digraphPlot.draw_board()
        # fig1 = ImageTk.PhotoImage(Image.open("sample_1.jpg"))
        fig = cv2.imread("sample_1.png")
        width, height = fig.shape[1], fig.shape[0]
        width_new = 1000
        fig_new = cv2.resize(fig, (width_new, int(height * width_new / width)))
        cv2.imwrite('fig_new_1.png', fig_new)
        b, g, r = cv2.split(fig_new)
        fig_new = cv2.merge((r, g, b))
        img = Image.fromarray(fig_new)
        im = ImageTk.PhotoImage(image=img)
        self._master.im = im
        self._digraphPlot.create_image(0, 0, anchor=tk.NW, image=im)
        self._master.tk.call('tk', 'scaling', 4.0)


class digraphPlot(tk.Canvas, tk.Frame):

    def __init__(self, master, delete_node=[], node_weight={}, node_ID={}):
        """
        Construct a board view from a board_layout.
        Parameters:
        master (tk.Widget): Widget within which the board is placed.
        adjacency_matrix (Matrix): The class BoardModel, the basic gameplay settings.
        board_width (int): The number of pixels the board should span (both width and height).
        """
        super().__init__(master)

        self._node_weight = node_weight
        self._node_ID = node_ID
        self._delete_node = delete_node
        self._master = master
        self._excel_name = self.load_excel()
        self._matrix = Matrix(self._excel_name, self._node_ID, self._node_weight)
        self._adjacency_matrix = self._matrix.adjacency_matrix()
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
        self._filename = filedialog.askopenfilename()
        # If file exists
        if self._filename:
            self._master.title(self._filename)
            self._excel_name = self._filename
            return self._filename

    def re_excel(self):

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
        quit = messagebox.askyesno("Quit", "Are you sure you want to quit ?")
        if quit:
            self._master.destroy()

    def draw_board(self):
        """Draw the game board by updating the rectangle displayed in each place."""
        self.plot_Digraph_initial()

    def get_dict(self, list1):
        output = dict([(i[0], i[1]) for i in list1])
        return output

    def get_Digraph(self):
        G = nx.DiGraph(directed=True)
        a = []
        for i in range(len(self._adjacency_matrix)):
            a.append(str(i))
        for i in range(len(self._adjacency_matrix)):
            for j in range(len(self._adjacency_matrix)):
                if self._adjacency_matrix[i][j] == 1:
                    G.add_edge(a[i], a[j], color='r', weight=int(self._adjacency_matrix[i][j]))
                elif self._adjacency_matrix[i][j] == 2:
                    G.add_edge(a[i], a[j], color='b', weight=int(self._adjacency_matrix[i][j]))
                elif self._adjacency_matrix[i][j] == 3:
                    G.add_edge(a[i], a[j], color='g', weight=int(self._adjacency_matrix[i][j]))
        return G

    def plot_Digraph_initial(self):
        fig = plt.figure(figsize=(6, 6), dpi=200)

        plt.axis('off')
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0,
                            hspace=0, wspace=0)
        self._digarph_normal = self.get_Digraph()
        pos = nx.nx_agraph.graphviz_layout(self._digarph_normal)
        colors = nx.get_edge_attributes(self._digarph_normal, 'color').values()
        # edge_labels = dict([((u, v,), d['weight'])
        #                   for u, v, d in G.edges(data=True)])
        # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        options = {'font_size': 3,
                   'font_color': 'white',
                   'node_color': 'black',
                   'node_size': 60,
                   'style': 'solid',  # (solid|dashed|dotted,dashdot)
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

    def get_Giant_Component(self):
        a = 0
        largest = max(nx.strongly_connected_components(self.get_Digraph()), key=len)
        for i in largest:
            a = int(i)
        self._largest_component.append(a)

    def neighbor_of_nodes(self):
        nodes = {}
        for i in range(len(self._adjacency_matrix)):
            node_neighbor = []
            for neighbor, value in enumerate(self._adjacency_matrix[i]):
                if value != 0:
                    node_neighbor.append(neighbor)
            if len(node_neighbor) != 0:
                nodes[i] = node_neighbor
        return nodes

    # input the value of first key inside neighbor of nodes
    def new(self, saved_list, component, index):
        if len(self._node_neighbor) == 0:
            return
        else:
            print(self._node_neighbor)
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

    def delete_by_degree(self):
        count = -1
        name = ''
        a = self.get_Digraph().degree
        while len(a) != 0:
            for i in a:
                if i[1] > count:
                    count = i[1]
                    name = i[0]
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self.get_Giant_Component()
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            count = -1
            name = ''
            a = self.get_Digraph().degree
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)):
            a.append(i)
        print(self._largest_component)
        sub1.plot(a, self._largest_component)
        y = np.array(self._largest_component)
        area = simps(y, dx=len(self._deleted_node))
        sub1.text(5, 25, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of degree')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Number of Remaining Nodes')
        fig1.savefig('Effectiveness_Degree.png')
        print("area =", area)

    def delete_by_degree_connected(self):
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
            self.new([],component,0)
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
        print(self._largest_connected_component)
        print(a)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of degree')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_Degree.png')
        print("area =", area)

    def delete_by_In_degree_connected(self):
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
        print(self._largest_connected_component)

        print(a)
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
        print(self._largest_connected_component)

        print(a)
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
            print(2)
            print(self._delete_node)
            print(2)
            self.new([], component, 0)
            for i in component:
                if len(i) > cc:
                    cc = len(i)
                    aa.append(i)
                    if len(aa) != 1:
                        aa.pop(0)
            print(cc)
            print(aa)
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
        print(self._largest_connected_component)
        print(a)
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
        print(self._largest_connected_component)
        print(a)
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
            print(2)
            print(self._delete_node)
            print(2)
            self.new([], component, 0)
            print(component)
            print(1)
            for i in component:
                if len(i) > cc:
                    cc = len(i)
                    aa.append(i)
                    if len(aa) != 1:
                        aa.pop(0)
            print(cc)
            print(aa)
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
        print(self._largest_connected_component)
        print(a)
        sub1.plot(a, self._largest_connected_component)
        y = np.array(self._largest_connected_component)
        area = int(simps(y, dx=len(self._deleted_node)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of Betweenness')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Size of Remaining Largest Component')
        fig1.savefig('Robustness_Betweenness.png')
        print("area =", area)

    def delete_by_indegree(self):
        count = 0
        name = ''
        a = self.get_Digraph().in_degree
        while len(a) != 0:
            for i in a:
                if i[1] > count:
                    count = i[1]
                    name = i[0]
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self.get_Giant_Component()
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            count = 0
            name = ''
            a = self.get_Digraph().in_degree
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)):
            a.append(i)
        sub1.plot(a, self._largest_component)
        y = np.array(self._largest_component)
        area = int(simps(y, dx=len(self._deleted_node)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of in_degree')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Number of Remaining Nodes')
        fig1.savefig('graph_in_degree_remove.png')

    def delete_by_outdegree(self):
        count = 0
        name = ''
        a = self.get_Digraph().out_degree
        while len(a) != 0:
            for i in a:
                if i[1] > count:
                    count = i[1]
                    name = i[0]
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self.get_Giant_Component()
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            count = 0
            name = ''
            a = self.get_Digraph().out_degree
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)):
            a.append(i)
        sub1.plot(a, self._largest_component)
        y = np.array(self._largest_component)
        area = int(simps(y, dx=len(self._deleted_node)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of out_degree')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Number of Remaining Nodes')
        fig1.savefig('graph_out_degree_remove.png')
        print("area =", area)

    def delete_by_eigenvector(self):
        count = 0
        name = ''
        b = len(self.get_Digraph())
        a = nx.eigenvector_centrality(self.get_Digraph(), tol=1e-03)
        while b != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self.get_Giant_Component()
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            count = 0
            name = ''
            if len(self.get_Digraph()) != 0:
                a = nx.eigenvector_centrality(self.get_Digraph(), tol=1e-03)
            else:
                break
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)):
            a.append(i)
        sub1.plot(a, self._largest_component)
        y = np.array(self._largest_component)
        area = int(simps(y, dx=len(self._deleted_node)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of eigenvector')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Number of Remaining Nodes')
        fig1.savefig('graph_eigenvector_remove.png')
        print("area =", area)

    def delete_by_closeness(self):
        count = 0
        name = ''
        a = nx.closeness_centrality(self.get_Digraph())
        while len(a) != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self.get_Giant_Component()
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            count = 0
            name = ''
            a = nx.closeness_centrality(self.get_Digraph())
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)):
            a.append(i)
        sub1.plot(a, self._largest_component)
        y = np.array(self._largest_component)
        area = int(simps(y, dx=len(self._deleted_node)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of closeness')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Number of Remaining Nodes')
        fig1.savefig('graph_closeness_remove.png')
        print("area =", area)

    def delete_by_betweenness(self):
        count = -1
        name = ''
        a = nx.betweenness_centrality(self.get_Digraph())
        while len(a) != 0:
            for i in a:
                if a[i] > count:
                    count = a[i]
                    name = i
            self._deleted_node.append(name)
            self._delete_node.append(int(name))
            self.get_Giant_Component()
            self._matrix.deleteNode(self._delete_node)
            self._delete_node = []
            self._adjacency_matrix = self._matrix.adjacency_matrix()
            count = -1
            name = ''
            a = nx.betweenness_centrality(self.get_Digraph())
        fig1, sub1 = plt.subplots()
        a = []
        for i in range(len(self._deleted_node)):
            a.append(i)
        sub1.plot(a, self._largest_component)
        y = np.array(self._largest_component)
        area = int(simps(y, dx=len(self._deleted_node)))
        sub1.text(20, 150, 'The area under curve is ' + str(area))
        sub1.set_title('Nodes elimination follows order of betweenness')
        sub1.set_xlabel('Number of Removed Nodes')
        sub1.set_ylabel('Number of Remaining Nodes')
        fig1.savefig('graph_betweenness_remove.png')
        print("area =", area)

    def plot_distribution(self, parameter, figure_number, title):
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

    def add_button(self):

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
        print(nx.eigenvector_centrality(self.get_Digraph(), max_iter=600))
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

        DeleteByDegree = tk.Button(self._frame_two, text="Effectiveness_Degree", width=50, activebackground="#33B5E5")
        DeleteByDegree.bind("<Button-1>", lambda evt: self.delete_by_degree())
        DeleteByDegree.pack()

        PlotDegree = tk.Button(self._frame_two, text="Effectiveness_In_Degree", width=50, activebackground="#33B5E5")
        PlotDegree.bind("<Button-1>", lambda evt: self.delete_by_indegree())
        PlotDegree.pack()

        PlotInDegree = tk.Button(self._frame_two, text="Effectiveness_Out_Degree", width=50, activebackground="#33B5E5")
        PlotInDegree.bind("<Button-1>", lambda evt: self.delete_by_outdegree())
        PlotInDegree.pack()

        PlotOutDegree = tk.Button(self._frame_two, text="Effectiveness_Closeness", width=50, activebackground="#33B5E5")
        PlotOutDegree.bind("<Button-1>", lambda evt: self.delete_by_closeness())
        PlotOutDegree.pack()

        PlotCloseness = tk.Button(self._frame_two, text="Effectiveness_Eigenvector", width=50, activebackground="#33B5E5")
        PlotCloseness.bind("<Button-1>", lambda evt: self.delete_by_eigenvector())
        PlotCloseness.pack()

        PlotEigenvector = tk.Button(self._frame_two, text="Effectiveness_Betweenness", width=50, activebackground="#33B5E5")
        PlotEigenvector.bind("<Button-1>", lambda evt: self.delete_by_betweenness())
        PlotEigenvector.pack()

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
        Degree = self.det_degree(Indegree,Outdegree)
        Degree_Distribution = tk.Button(self._frame_two, text="Degree_Distribution", width=50,
                                          activebackground="#33B5E5")
        Degree_Distribution.bind("<Button-1>", lambda evt: self.plot_distribution(Degree,1,"Degree_Distribution"))
        Degree_Distribution.pack()

        In_Degree_Distribution = tk.Button(self._frame_two, text="Indegree_Distribution", width=50,
                                          activebackground="#33B5E5")
        In_Degree_Distribution.bind("<Button-1>", lambda evt: self.plot_distribution(self.det_indegree(),2,"In_Degree_Distribution"))
        In_Degree_Distribution.pack()

        Out_Degree_Distribution = tk.Button(self._frame_two, text="Outdegree_Distribution", width=50,
                                          activebackground="#33B5E5")
        Out_Degree_Distribution.bind("<Button-1>", lambda evt: self.plot_distribution(self.det_outdegree(),3,"Out_Degree_Distribution"))
        Out_Degree_Distribution.pack()

        betweenness_values = []
        closeness_centrality_values = []
        Eigenvector_Centrality_values = []


        closeness_centrality_Distribution = tk.Button(self._frame_two, text="Closeness_Distribution", width=50,
                                          activebackground="#33B5E5")
        closeness_centrality_Distribution.bind("<Button-1>", lambda evt: self.plot_distribution(self.det_closeness_one(closeness_centrality_values),4,"Closeness_Distribution"))
        closeness_centrality_Distribution.pack()

        Eigenvector_Distribution = tk.Button(self._frame_two, text="Eigenvector_Distribution", width=50,
                                          activebackground="#33B5E5")
        Eigenvector_Distribution.bind("<Button-1>", lambda evt: self.plot_distribution(self.det_eigenvector_one(Eigenvector_Centrality_values), 5, "Eigenvector_Distribution"))
        Eigenvector_Distribution.pack()

        Betweenness_Distribution = tk.Button(self._frame_two, text="Betweenness_Distribution", width=50,
                                          activebackground="#33B5E5")
        Betweenness_Distribution.bind("<Button-1>", lambda evt: self.plot_distribution(self.det_betweenness_one(betweenness_values),6,"Betweenness_Distribution"))
        Betweenness_Distribution.pack()


    def det_betweenness_one(self,betweenness_values):
        for k in range(len(nx.betweenness_centrality(self.get_Digraph()))):
            betweenness_values.append(nx.betweenness_centrality(self.get_Digraph()).get(str(k)))
        return betweenness_values

    def det_eigenvector_one(self,Eigenvector_Centrality_values):
        for n in range(len(nx.eigenvector_centrality(self.get_Digraph(),tol=1e-03,max_iter=600))):
            Eigenvector_Centrality_values.append(nx.eigenvector_centrality(self.get_Digraph(),tol=1e-03,max_iter=600).get(str(n)))
        return Eigenvector_Centrality_values

    def det_closeness_one(self,closeness_centrality_values):
        for m in range(len(nx.closeness_centrality(self.get_Digraph()))):
            closeness_centrality_values.append(nx.closeness_centrality(self.get_Digraph()).get(str(m)))
        return closeness_centrality_values
    def entryValueRemove(self):
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
