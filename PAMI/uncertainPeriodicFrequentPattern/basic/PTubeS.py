#  Copyright (C)  2021 Rage Uday Kiran
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
from  abstract import *

minSup = float()
maxPer = float()
lno = int()
first = int()
last = int()
periodic = {}


class Item:
    """
        A class used to represent the item with probability in transaction of dataset

        ...

        Attributes
        __________
        item : int or word
            Represents the name of the item
        probability : float
            Represent the existential probability(likelihood presence) of an item
    """

    def __init__(self, item, probability):
        self.item = item
        self.probability = probability


class Node(object):
    """
        A class used to represent the node of frequentPatternTree

        Attributes
        ----------
        item : int
            storing item name of a node
        probability : int
            To maintain the existence probability of node
        secondProbability:
            To maintain the second probability of a node
        parent : node
            To maintain the parent of every node
        children : list
            To maintain the children of node
        timeStamps:
            To maintain the timeStamps of a node

        Methods
        -------

        addChild(itemName)
            storing the children to their respective parent nodes
    """

    def __init__(self, item, children):
        self.item = item
        self.probability = 1
        self.secondProbability = 1
        self.children = children
        self.parent = None
        self.timeStamps = []

    def addChild(self, node):
        """
        To add the children details to the parent node
        :param node: children node
        :return: updated parent node children
        """
        self.children[node.item] = node
        node.parent = self


def Second(transaction, i):
    """
    To find the secondProbability of a node in transaction by considering second max probability
    of the prefix items.
    :param transaction: transaction in a database with item and probability
    :param i: index of the item to calculate secondProbability in a transaction
    :return: secondProbability of a node
    """
    temp = []
    for j in range(0, i):
        temp.append(transaction[j].probability)
    l1 = max(temp)
    temp.remove(l1)
    l2 = max(temp)
    return l2


def printTree(root):
    """
    To print the details of nodes in tree 
    :param root: root node of tree
    :return: details nodes in depth-first order
    """
    for x, y in root.children.items():
        print(x, y.item, y.probability, y.parent.item, y.timeStamps, y.secondProbability)
        printTree(y)


class Tree(object):
    """
        A class used to represent the frequentPatternGrowth tree structure

        ...

        Attributes
        ----------
        root : Node
            Represents the root node of the tree
        summaries : dictionary
            storing the nodes with same item name
        info : dictionary
            stores the support of items


        Methods
        -------
        addTransaction(transaction)
            creating transaction as a branch in frequentPatternTree
        addConditionalTransaction(prefixPaths, supportOfItems)
            construct the conditional tree for prefix paths
        getConditionalPatterns(Node)
            generates the conditional patterns from tree for specific node
        conditionalTransactions(prefixPaths,Support)
            takes the prefixPath of a node and support at child of the path and extract the frequent items from
            prefixPaths and generates prefixPaths with items which are frequent
        removeNode(node)
            removes the node from tree once after generating all the patterns respective to the node
        generatePatterns(Node)
            starts from the root node of the tree and mines the frequent patterns

    """

    def __init__(self):
        self.root = Node(None, {})
        self.summaries = {}
        self.info = {}

    def addTransaction(self, transaction, tid):
        """adding transaction into tree

            :param transaction : it represents the one transactions in database
            :type transaction : list
            :param tid : the timestamp of transaction
            :type tid : list
        """
        currentNode = self.root
        k = 0
        for i in range(len(transaction)):
            k += 1
            if transaction[i].item not in currentNode.children:
                newNode = Node(transaction[i].item, {})
                newNode.k = k
                if k >= 3:
                    newNode.secondProbability = Second(transaction, i)
                l1 = i - 1
                temp = []
                while l1 >= 0:
                    temp.append(transaction[l1].probability)
                    l1 -= 1
                if len(temp) == 0:
                    newNode.probability = round(transaction[i].probability, 2)
                else:
                    newNode.probability = round(max(temp) * transaction[i].probability, 2)
                currentNode.addChild(newNode)
                if transaction[i].item in self.summaries:
                    self.summaries[transaction[i].item].append(newNode)
                else:
                    self.summaries[transaction[i].item] = [newNode]
                currentNode = newNode
            else:
                currentNode = currentNode.children[transaction[i].item]
                if k >= 3:
                    currentNode.secondProbability = max(transaction[i].probability, currentNode.secondProbability)
                currentNode.k = k
                l1 = i - 1
                temp = []
                while l1 >= 0:
                    temp.append(transaction[l1].probability)
                    l1 -= 1
                if len(temp) == 0:
                    currentNode.probability += round(transaction[i].probability, 2)
                else:
                    nn = max(temp) * transaction[i].probability
                    currentNode.probability += round(nn, 2)
        currentNode.timeStamps = currentNode.timeStamps + tid

    def addConditionalTransaction(self, transaction, tid, sup, second):
        """constructing conditional tree from prefixPaths

                :param transaction : it represents the one transactions in database
                :type transaction : list
                :param tid : timestamps of a pattern or transaction in tree
                :param tid : list
                :param sup : support of prefixPath taken at last child of the path
                :type sup : list
                :param second: second probability of node stores max second probability
                :type second float
        """
        currentNode = self.root
        k = 0
        for i in range(len(transaction)):
            k += 1
            if transaction[i] not in currentNode.children:
                newNode = Node(transaction[i], {})
                newNode.k = k
                newNode.secondProbability = second
                newNode.probability = sup
                currentNode.addChild(newNode)
                if transaction[i] in self.summaries:
                    self.summaries[transaction[i]].append(newNode)
                else:
                    self.summaries[transaction[i]] = [newNode]
                currentNode = newNode
            else:
                currentNode = currentNode.children[transaction[i]]
                currentNode.k = k
                currentNode.secondProbability = max(currentNode.secondProbability, second)
                currentNode.probability += sup
        currentNode.timeStamps = currentNode.timeStamps + tid

    def getConditionalPatterns(self, alpha):
        """generates all the conditional patterns of respective node

                        :param alpha : it represents the Node in tree
                        :type alpha : Node
                                        """
        finalPatterns = []
        finalTimeStamps = []
        sup = []
        second = []
        for i in self.summaries[alpha]:
            set1 = i.timeStamps
            s = i.probability
            s1 = i.secondProbability
            set2 = []
            while i.parent.item is not None:
                set2.append(i.parent.item)
                i = i.parent
            if len(set2) > 0:
                set2.reverse()
                finalPatterns.append(set2)
                finalTimeStamps.append(set1)
                second.append(s1)
                sup.append(s)
        finalPatterns, finalTimeStamps, support, info = conditionalTransactions(finalPatterns, finalTimeStamps, sup)
        return finalPatterns, finalTimeStamps, support, info, second

    def removeNode(self, nodeValue):
        """removing the node from tree

                        :param nodeValue : it represents the node in tree
                        :type nodeValue : node
                                       """
        for i in self.summaries[nodeValue]:
            i.parent.timeStamps = i.parent.timeStamps + i.timeStamps
            del i.parent.children[nodeValue]

    def getTimeStamps(self, alpha):
        """
        To get the timeStamps of a node in tree
        :param alpha: node of a tree
        :return: timeStamps of a node
        """
        temp = []
        for i in self.summaries[alpha]:
            temp += i.timeStamps
        return temp

    def generatePatterns(self, prefix):
        """generates the patterns

                                        :param prefix : forms the combination of items
                                        :type prefix : list
                                        """
        global periodic, minSup
        for i in sorted(self.summaries, key=lambda x: (self.info.get(x)[0])):
            pattern = prefix[:]
            pattern.append(i)
            s = 0
            for x in self.summaries[i]:
                if x.k <= 2:
                    s += x.probability
                elif x.k >= 3:
                    n = x.probability * pow(x.secondProbability, (x.k - 2))
                    s += n
            periodic[tuple(pattern)] = self.info[i]
            if s >= minSup:
                patterns, timeStamps, support, info, second = self.getConditionalPatterns(i)
                conditionalTree = Tree()
                conditionalTree.info = info.copy()
                for pat in range(len(patterns)):
                    conditionalTree.addConditionalTransaction(patterns[pat], timeStamps[pat], support[pat], second[pat])
                if len(patterns) > 0:
                    conditionalTree.generatePatterns(pattern)
            self.removeNode(i)


def getPeriodAndSupport(s, timeStamps):
    """
    To calculate the support and periodicity of timeStamps
    :param s: support
    :param timeStamps: timeStamps
    :return: support and periodicity of timeStamps
    """
    global lno, maxPer
    timeStamps.sort()
    cur = 0
    per = 0
    sup = s
    for j in range(len(timeStamps)):
        per = max(per, timeStamps[j] - cur)
        if per > maxPer:
            return [0, 0]
        cur = timeStamps[j]
    per = max(per, lno - cur)
    return [sup, per]


def conditionalTransactions(conditionalPatterns, conditionalTimeStamps, support):
    """ It generates the conditional patterns with frequent items

        :param conditionalPatterns : conditional patterns generated from getConditionalPatterns method for respective node
        :type conditionalPatterns : list
        :param conditionalTimeStamps : timestamps of respective conditional timestamps
        :type conditionalTimeStamps : list
        :param support : the support of conditional pattern in tree
        :type support : list
    """
    global minSup, maxPer
    pat = []
    timeStamps = []
    sup = []
    data1 = {}
    count = {}
    for i in range(len(conditionalPatterns)):
        for j in conditionalPatterns[i]:
            if j in data1:
                data1[j] = data1[j] + conditionalTimeStamps[i]
                count[j] += support[i]
            else:
                data1[j] = conditionalTimeStamps[i]
                count[j] = support[i]
    updatedDict = {}
    for m in data1:
        updatedDict[m] = getPeriodAndSupport(count[m], data1[m])
    updatedDict = {k: v for k, v in updatedDict.items() if v[0] >= minSup and v[1] <= maxPer}
    count = 0
    for p in conditionalPatterns:
        p1 = [v for v in p if v in updatedDict]
        trans = sorted(p1, key=lambda x: (updatedDict.get(x)[0]), reverse=True)
        if len(trans) > 0:
            pat.append(trans)
            timeStamps.append(conditionalTimeStamps[count])
            sup.append(support[count])
        count += 1
    return pat, timeStamps, sup, updatedDict


class PTubeS(periodicFrequentPatterns):
    """
        Periodic-TubeS is  to discover periodic-frequent patterns in a temporal database.

        Reference:
        --------

       Attributes
        ----------
        iFile : file
            Name of the Input file to mine complete set of periodic-frequent patterns
        oFile : file
            Name of the output file to store complete set of periodic-frequent patterns
        memoryUSS : float
            To store the total amount of USS memory consumed by the program
        memoryRSS : float
            To store the total amount of RSS memory consumed by the program
        startTime:float
            To record the start time of the mining process
        endTime:float
            To record the completion time of the mining process
        minSup : int/float
            The user given minimum support
        maxPer : int/float
            The user given maximum period
        Database : list
            To store the transactions of a database in list
        mapSupport : Dictionary
            To maintain the information of item and their frequency
        lno : int
            To represent the total no of transaction
        tree : class
            To represents the Tree class
        itemSetCount : int
            To represents the total no of patterns
        finalPatterns : dict
            To store the complete patterns
        Methods
        -------
        startMine()
            Mining process will start from here
        getPeriodicFrequentPatterns()
            Complete set of patterns will be retrieved with this function
        storePatternsInFile(oFile)
            Complete set of periodic-frequent patterns will be loaded in to a output file
        getPatternsInDataFrame()
            Complete set of periodic-frequent patterns will be loaded in to a dataframe
        getMemoryUSS()
            Total amount of USS memory consumed by the mining process will be retrieved from this function
        getMemoryRSS()
            Total amount of RSS memory consumed by the mining process will be retrieved from this function
        getRuntime()
            Total amount of runtime taken by the mining process will be retrieved from this function
        creatingItemSets(fileName)
            Scans the dataset and stores in a list format
        PeriodicFrequentOneItem()
            Extracts the one-periodic-frequent patterns from database
        updateDatabases()
            Update the database by removing aperiodic items and sort the Database by item decreased support
        buildTree()
            After updating the Database, remaining items will be added into the tree by setting root node as null
        convert()
            to convert the user specified value
        startMine()
            Mining process will start from this function
        Executing the code on terminal:
        -------
        Format:
        ------
        python3 PTubeS.py <inputFile> <outputFile> <minSup> <maxPer>
        Examples:
        --------
        python3 PTubeS.py sampleTDB.txt patterns.txt 0.3 4     (minSup and maxPer will be considered in support count or frequency)

        Sample run of importing the code:
        -------------------

        from PAMI.uncertainPeriodicFrequentPattern.basic import PTubeS as alg

        obj = alg.PTubeS(iFile, minSup, maxPer)

        obj.startMine()

        periodicFrequentPatterns = obj.getPeriodicFrequentPatterns()

        print("Total number of Periodic Frequent Patterns:", len(periodicFrequentPatterns))

        obj.storePatternsInFile(oFile)

        Df = obj.getPatternsInDataFrame()

        memUSS = obj.getMemoryUSS()

        print("Total Memory in USS:", memUSS)

        memRSS = obj.getMemoryRSS()

        print("Total Memory in RSS", memRSS)

        run = obj.getRuntime()

        print("Total ExecutionTime in seconds:", run)

        Credits:
        -------
        The complete program was written by P.Likhitha  under the supervision of Professor Rage Uday Kiran.\n

    """

    rank = {}
    startTime = float()
    endTime = float()
    minSup = float()
    maxPer = float()
    finalPatterns = {}
    iFile = " "
    oFile = " "
    memoryUSS = float()
    memoryRSS = float()
    Database = []
    lno = 0

    def creatingItemSets(self):
        """
            Storing the complete transactions of the database/input file in a database variable


        """
        try:
            with open(self.iFile, 'r') as f:
                for line in f:
                    temp = [i.rstrip() for i in line.split("\t")]
                    tr = [int(temp[0])]
                    for i in temp[1:]:
                        i1 = i.index('(')
                        i2 = i.index(')')
                        item = i[0:i1]
                        probability = float(i[i1 + 1:i2])
                        product = Item(item, probability)
                        tr.append(product)
                    self.lno += 1
                    self.Database.append(tr)
        except IOError:
            print("File Not Found")

    def scanDatabase(self):
        """takes the transactions and calculates the support of each item in the dataset and assign the
            ranks to the items by decreasing support and returns the frequent items list

        """
        global first, last
        mapSupport = {}
        for i in self.Database:
            n = i[0]
            for j in i[1:]:
                if j.item not in mapSupport:
                    mapSupport[j.item] = [round(j.probability, 2), abs(first - n), n]
                else:
                    mapSupport[j.item][0] += round(j.probability, 2)
                    mapSupport[j.item][1] = max(mapSupport[j.item][1], abs(n - mapSupport[j.item][2]))
                    mapSupport[j.item][2] = n
        for key in mapSupport:
            mapSupport[key][1] = max(mapSupport[key][1], last - mapSupport[key][2])
        mapSupport = {k: [round(v[0], 2), v[1]] for k, v in mapSupport.items() if
                      v[1] <= self.maxPer and v[0] >= self.minSup}
        plist = [k for k, v in sorted(mapSupport.items(), key=lambda x: (x[1][0], x[0]), reverse=True)]
        self.rank = dict([(index, item) for (item, index) in enumerate(plist)])
        return mapSupport, plist

    def buildTree(self, data, info):
        """it takes the transactions and support of each item and construct the main tree with setting root
                                    node as null

                :param data : it represents the one transactions in database
                :type data : list
                :param info : it represents the support of each item
                :type info : dictionary
            """
        rootNode = Tree()
        rootNode.info = info.copy()
        for i in range(len(data)):
            set1 = [data[i][0]]
            rootNode.addTransaction(data[i][1:], set1)
        return rootNode

    def updateTransactions(self, dict1):
        """remove the items which are not frequent from transactions and updates the transactions with rank of items

                :param dict1 : frequent items with support
                :type dict1 : dictionary
        """
        list1 = []
        for tr in self.Database:
            list2 = [int(tr[0])]
            for i in range(1, len(tr)):
                if tr[i].item in dict1:
                    list2.append(tr[i])
            if (len(list2) >= 2):
                basket = list2[1:]
                basket.sort(key=lambda val: self.rank[val.item])
                list2[1:] = basket[0:]
                list1.append(list2)
        return list1

    def check(self, i, x):
        """To check the presence of item or pattern in transaction

                    :param x: it represents the pattern
                    :type x : list
                    :param i : represents the uncertain transactions
                    :type i : list
        """
        for m in x:
            k = 0
            for n in i:
                if m == n.item:
                    k += 1
            if k == 0:
                return 0
        return 1

    def convert(self, value):
        """
            To convert the given user specified value
            :param value: user specified value
            :return: converted value
        """
        if type(value) is int:
            value = int(value)
        if type(value) is float:
            value = float(value)
        if type(value) is str:
            if '.' in value:
                value = float(value)
            else:
                value = int(value)

        return value

    def removeFalsePositives(self):
        """
        To remove false positives in generated patterns
        :return: original patterns
        """
        periods = {}
        for i in self.Database:
            for x, y in periodic.items():
                if len(x) == 1:
                    periods[x] = y[0]
                else:
                    s = 1
                    check = self.check(i[1:], x)
                    if check == 1:
                        for j in i[1:]:
                            if j.item in x:
                                s *= j.probability
                        if x in periods:
                            periods[x] += s
                        else:
                            periods[x] = s
        for x, y in periods.items():
            if y >= minSup:
                sample = str()
                for i in x:
                    sample = sample + i + " " 
                self.finalPatterns[sample] = y

    def startMine(self):
        """Main method where the patterns are mined by constructing tree and remove the remove the false patterns
                                   by counting the original support of a patterns


                       """
        global lno, first, last, minSup, maxPer
        self.startTime = time.time()
        self.creatingItemSets()
        self.minSup = self.convert(self.minSup)
        self.maxPer = self.convert(self.maxPer)
        minSup, maxPer, lno = self.minSup, self.maxPer, self.lno
        mapSupport, plist = self.scanDatabase()
        updatedTrans = self.updateTransactions(mapSupport)
        info = {k: v for k, v in mapSupport.items()}
        Tree = self.buildTree(updatedTrans, info)
        Tree.generatePatterns([])
        self.removeFalsePositives()
        print("periodic Frequent patterns were generated successfully using Periodic-TubeS algorithm")
        self.endTime = time.time()
        process = psutil.Process(os.getpid())
        self.memoryUSS = process.memory_full_info().uss
        self.memoryRSS = process.memory_info().rss

    def getMemoryUSS(self):
        """Total amount of USS memory consumed by the mining process will be retrieved from this function

        :return: returning USS memory consumed by the mining process
        :rtype: float
        """

        return self.memoryUSS

    def getMemoryRSS(self):
        """Total amount of RSS memory consumed by the mining process will be retrieved from this function

        :return: returning RSS memory consumed by the mining process
        :rtype: float
        """

        return self.memoryRSS

    def getRuntime(self):
        """Calculating the total amount of runtime taken by the mining process


        :return: returning total amount of runtime taken by the mining process
        :rtype: float
        """

        return self.endTime - self.startTime

    def getPatternsInDataFrame(self):
        """Storing final frequent patterns in a dataframe

        :return: returning frequent patterns in a dataframe
        :rtype: pd.DataFrame
        """

        dataframe = {}
        data = []
        for a, b in self.finalPatterns.items():
            data.append([a, b[0], b[1]])
            dataframe = pd.DataFrame(data, columns=['Patterns', 'Support', 'Periodicity'])
        return dataframe

    def storePatternsInFile(self, outFile):
        """Complete set of frequent patterns will be loaded in to a output file

        :param outFile: name of the output file
        :type outFile: file
        """
        self.oFile = outFile
        writer = open(self.oFile, 'w+')
        for x, y in self.finalPatterns.items():
            s1 = x + ":" + str(y)
            writer.write("%s \n" % s1)

    def getPeriodicFrequentPatterns(self):
        """ Function to send the set of frequent patterns after completion of the mining process

        :return: returning frequent patterns
        :rtype: dict
        """
        return self.finalPatterns


if __name__ == "__main__":
    if len(sys.argv) is 5:
        ap = PTubeS(sys.argv[1], sys.argv[3], sys.argv[4])
        ap.startMine()
        frequentPatterns = ap.getPeriodicFrequentPatterns()
        print("Total number of Frequent Patterns:", len(frequentPatterns))
        ap.storePatternsInFile(sys.argv[2])
        memUSS = ap.getMemoryUSS()
        print("Total Memory in USS:", memUSS)
        memRSS = ap.getMemoryRSS()
        print("Total Memory in RSS", memRSS)
        run = ap.getRuntime()
    else:
        print("Error! The number of input parameters do not match the total number of parameters provided")
