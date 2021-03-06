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
from itertools import combinations
from  abstract import *

pfList = []
minSup = str()
maxPer = str()
lno = int()


class Interval(object):
    """
        To represent the timestamp interval of a node in summaries
    """

    def __init__(self, start, end, per, sup):
        self.start = start
        self.end = end
        self.per = per
        self.sup = sup


class NodeSummaries(object):
    """
        To define the summaries of timeStamps of a node
        
       Attributes
        ----------
        totalSummaries : list
            stores the summaries of timestamps
                
        Methods
        -------
        insert(timeStamps)
            inserting and merging the timestamps into the summaries of a node
    """

    def __init__(self):
        self.totalSummaries = []

    def insert(self, tid):
        """ To insert and merge the timeStamps into summaries of a node

            :param tid: timeStamps of a node
            :return: summaries of a node
        """
        k = self.totalSummaries[-1]
        diff = tid - k.end
        if diff <= maxPer:
            k.end = tid
            k.per = max(diff, k.per)
            #             print(k.per)
            k.sup += 1
        else:
            self.totalSummaries.append(Interval(tid, tid, 0, 1))
        return self.totalSummaries


def merge(summariesX, summariesY):
    """To Merge the timeStamps

    :param summariesX:  TimeStamps of an one itemSet
    :param summariesY:  TimeStamps of an one itemSet
    :return:  Merged timestamp of both itemSets
    """
    iter1 = 0
    iter2 = 0
    updatedSummaries = []
    l1 = len(summariesX)
    l2 = len(summariesY)
    while 1:
        if summariesX[iter1].start < summariesY[iter2].start:
            if summariesX[iter1].end < summariesY[iter2].start:
                diff = summariesY[iter2].start - summariesX[iter1].end
                if diff > maxPer:
                    updatedSummaries.append(Interval(summariesX[iter1].start,
                                                     summariesX[iter1].end, summariesX[iter1].per,
                                                     summariesX[iter1].sup))
                    iter1 += 1
                    if iter1 >= l1:
                        ck = 1
                        break
                else:
                    per1 = max(diff, summariesX[iter1].per)
                    per1 = max(per1, summariesY[iter2].per)
                    updatedSummaries.append(
                        Interval(summariesX[iter1].start, summariesY[iter2].end, per1,
                                 summariesX[iter1].sup + summariesY[iter2].sup))
                    iter1 += 1
                    iter2 += 1
                    if iter1 >= l1:
                        ck = 1
                        break

                    if iter2 >= l2:
                        ck = 2
                        break

            else:
                if summariesX[iter1].end > summariesY[iter2].end:
                    updatedSummaries.append(Interval(summariesX[iter1].start, summariesX[iter1].end,
                                                     summariesX[iter1].per,
                                                     summariesX[iter1].sup + summariesY[iter2].sup))
                else:
                    per1 = max(summariesX[iter1].per, summariesY[iter2].per)
                    updatedSummaries.append(
                        Interval(summariesX[iter1].start, summariesY[iter2].end, per1,
                                 summariesX[iter1].sup + summariesY[iter2].sup))
                iter1 += 1
                iter2 += 1
                if iter1 >= l1:
                    ck = 1
                    break

                if iter2 >= l2:
                    ck = 2
                    break
        else:
            if summariesY[iter2].end < summariesX[iter1].start:
                diff = summariesX[iter1].start - summariesY[iter2].end
                if diff > maxPer:
                    updatedSummaries.append(Interval(summariesY[iter2].start, summariesY[iter2].end,
                                                     summariesY[iter2].per, summariesY[iter2].sup))
                    iter2 += 1
                    if iter2 >= l2:
                        ck = 2
                        break
                else:
                    per1 = max(diff, summariesY[iter2].per)
                    per1 = max(per1, summariesX[iter1].per)
                    updatedSummaries.append(
                        Interval(summariesY[iter2].start, summariesX[iter1].end, per1,
                                 summariesY[iter2].sup + summariesX[iter1].sup))
                    iter2 += 1
                    iter1 += 1
                    if iter2 >= l2:
                        ck = 2
                        break

                    if iter1 >= l1:
                        ck = 1
                        break

            else:
                if summariesY[iter2].end > summariesX[iter1].end:
                    updatedSummaries.append(Interval(summariesY[iter2].start, summariesY[iter2].end,
                                                     summariesY[iter2].per,
                                                     summariesY[iter2].sup + summariesX[iter1].sup))
                else:
                    per1 = max(summariesY[iter2].per, summariesX[iter1].per)
                    updatedSummaries.append(
                        Interval(summariesY[iter2].start, summariesX[iter1].end, per1,
                                 summariesY[iter2].sup + summariesX[iter1].sup))
                iter2 += 1
                iter1 += 1
                if iter2 >= l2:
                    ck = 2
                    break

                if iter1 >= l1:
                    ck = 1
                    break
    if ck == 1:
        while iter2 < l2:
            updatedSummaries.append(summariesY[iter2])
            iter2 += 1
    else:
        while iter1 < l1:
            updatedSummaries.append(summariesX[iter1])
            iter1 += 1
    updatedSummaries = update(updatedSummaries)

    return updatedSummaries


def update(updatedSummaries):
    """ After updating the summaries with first, last, and period elements in summaries

    :param updatedSummaries: summaries that have been merged
    :return: updated summaries of a node
    """
    summaries = [updatedSummaries[0]]
    cur = updatedSummaries[0]
    for i in range(1, len(updatedSummaries)):
        v = (updatedSummaries[i].start - cur.end)
        if cur.end > updatedSummaries[i].start or v <= maxPer:
            cur.end = max(updatedSummaries[i].end, cur.end)
            cur.sup += updatedSummaries[i].sup
            cur.per = max(cur.per, updatedSummaries[i].per)
            cur.per = max(cur.per, v)
        else:
            summaries.append(updatedSummaries[i])
        cur = summaries[-1]
    return summaries


class Node(object):
    """ A class used to represent the node of frequentPatternTree



               Attributes
                ----------
                item : int
                    storing item of a node
                timeStamps : list
                    To maintain the timeStamps of Database at the end of the branch
                parent : node
                    To maintain the parent of every node
                children : list
                    To maintain the children of node

                Methods
                -------

                addChild(itemName)
                    storing the children to their respective parent nodes
            """

    def __init__(self, item, children):
        """ Initializing the Node class

        :param item: Storing the item of a node
        :type item: int
        :param children: To maintain the children of a node
        :type children: dict
        """
        self.item = item
        self.children = children
        self.parent = None
        self.timeStamps = NodeSummaries()

    def addChild(self, node):
        """
        Appends the children node details to a parent node

        :param node: children node
        :return: appending children node to parent node
        """
        self.children[node.item] = node
        node.parent = self


class Tree(object):
    """
        A class used to represent the frequentPatternGrowth tree structure


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
            addTransaction(Database)
                creating Database as a branch in frequentPatternTree
            addConditionalTransactions(prefixPaths, supportOfItems)
                construct the conditional tree for prefix paths
            getConditionalPatterns(Node)
                generates the conditional patterns from tree for specific node
            conditionalTransaction(prefixPaths,Support)
                takes the prefixPath of a node and support at child of the path and extract the frequent items from
                prefixPaths and generates prefixPaths with items which are frequent
            remove(Node)
                removes the node from tree once after generating all the patterns respective to the node
            generatePatterns(Node)
                starts from the root node of the tree and mines the periodic-frequent patterns

        """

    def __init__(self):
        self.root = Node(None, {})
        self.summaries = {}
        self.info = {}

    def addTransaction(self, transaction, tid):
        """
               Adding transaction into the tree

                       :param transaction: it represents the one transactions in a database
                       :type transaction: list
                       :param tid: represents the timestamp of a transaction
                       :type tid: list
               """
        currentNode = self.root
        for i in range(len(transaction)):
            if transaction[i] not in currentNode.children:
                newNode = Node(transaction[i], {})
                currentNode.addChild(newNode)
                if transaction[i] in self.summaries:
                    self.summaries[transaction[i]].append(newNode)
                else:
                    self.summaries[transaction[i]] = [newNode]
                currentNode = newNode
            else:
                currentNode = currentNode.children[transaction[i]]
        if len(currentNode.timeStamps.totalSummaries) != 0:
            currentNode.timeStamps.insert(tid)
        else:
            currentNode.timeStamps.totalSummaries.append(Interval(tid, tid, 0, 1))

    def addConditionalPatterns(self, transaction, tid):
        """
        To add the conditional transactions in to conditional tree

        :param transaction: conditional transaction list of a node
        :param tid: timestamp of a conditional transaction
        :return: the conditional tree of a node
        """
        currentNode = self.root
        for i in range(len(transaction)):
            if transaction[i] not in currentNode.children:
                newNode = Node(transaction[i], {})
                currentNode.addChild(newNode)
                if transaction[i] in self.summaries:
                    self.summaries[transaction[i]].append(newNode)
                else:
                    self.summaries[transaction[i]] = [newNode]
                currentNode = newNode
            else:
                currentNode = currentNode.children[transaction[i]]
        if len(currentNode.timeStamps.totalSummaries) != 0:
            currentNode.timeStamps.totalSummaries = merge(currentNode.timeStamps.totalSummaries, tid)
        else:
            currentNode.timeStamps.totalSummaries = tid

    def getConditionalPatterns(self, alpha):
        """
        To mine the conditional patterns of a node

        :param alpha: starts from the leaf node of a tree
        :return: the conditional patterns of a node
        """
        finalPatterns = []
        finalSets = []
        for i in self.summaries[alpha]:
            set1 = i.timeStamps.totalSummaries
            set2 = []
            while i.parent.item is not None:
                set2.append(i.parent.item)
                i = i.parent
            if len(set2) > 0:
                set2.reverse()
                finalPatterns.append(set2)
                finalSets.append(set1)
        finalPatterns, finalSets, info = conditionalTransactions(finalPatterns, finalSets)
        return finalPatterns, finalSets, info

    def removeNode(self, nodeValue):
        """
        to remove the node from the tree by pushing the timeStamps of leaf node to the parent node

        :param nodeValue: name of node to be deleted
        :return: removes the node from the tree
        """
        for i in self.summaries[nodeValue]:
            if len(i.parent.timeStamps.totalSummaries) != 0:
                i.parent.timeStamps.totalSummaries = merge(i.parent.timeStamps.totalSummaries,
                                                           i.timeStamps.totalSummaries)
            else:
                i.parent.timeStamps.totalSummaries = i.timeStamps.totalSummaries
            del i.parent.children[nodeValue]
            del i
        del self.summaries[nodeValue]

    def getTimeStamps(self, alpha):
        """
        To get the timeStamps of a respective node

        :param alpha: name of node for the timeStamps
        :return: timeStamps of a node
        """
        temp = []
        for i in self.summaries[alpha]:
            temp += i.timeStamps
        return temp

    def check(self):
        """
        To the total number of child and their summaries
        """
        k = self.root
        while len(k.children) != 0:
            if len(k.children) > 1:
                return 1
            if len(k.children) != 0 and len(k.timeStamps.totalSummaries) > 0:
                return 1
            for j in k.children:
                v = k.children[j]
                k = v
        return -1

    def generatePatterns(self, prefix):
        """
        Generating the patterns from the tree

        :param prefix: empty list to form the combinations
        :return: returning the periodic-frequent patterns from the tree
        """
        global pfList
        for i in sorted(self.summaries, key=lambda x: (self.info.get(x)[0], -x)):
            pattern = prefix[:]
            pattern.append(pfList[i])
            yield pattern, self.info[i]
            patterns, timeStamps, info = self.getConditionalPatterns(i)
            conditionalTree = Tree()
            conditionalTree.info = info.copy()
            for pat in range(len(patterns)):
                conditionalTree.addConditionalPatterns(patterns[pat], timeStamps[pat])
            find = conditionalTree.check()
            if find == 1:
                del patterns, timeStamps, info
                for cp in conditionalTree.generatePatterns(pattern):
                    yield cp
            else:
                if len(conditionalTree.info) != 0:
                    j = []
                    for r in timeStamps:
                        j += r
                    inf = getPeriodAndSupport(j)
                    patterns[0].reverse()
                    upp = []
                    for jm in patterns[0]:
                        upp.append(pfList[jm])
                    allSubsets = subLists(upp)
                    # print(upp,inf)
                    for pa in allSubsets:
                        yield pattern + pa, inf
                del patterns, timeStamps, info
                del conditionalTree
            self.removeNode(i)


def subLists(itemSet):
    """
    Forms all the subsets of given itemSet

    :param itemSet: itemSet or a list of periodic-frequent items
    :return: subsets of itemSet
    """
    subs = []
    for i in range(1, len(itemSet) + 1):
        temp = [list(x) for x in combinations(itemSet, i)]
        if len(temp) > 0:
            subs.extend(temp)

    return subs


def getPeriodAndSupport(timeStamps):
    """
    Calculates the period and support of list of timeStamps

    :param timeStamps: timeStamps of a  pattern or item
    :return: support and periodicity
    """
    cur = 0
    per = 0
    sup = 0
    for j in range(len(timeStamps)):
        per = max(per, timeStamps[j].start - cur)
        per = max(per, timeStamps[j].per)
        if per > maxPer:
            return [0, 0]
        cur = timeStamps[j].end
        sup += timeStamps[j].sup
    per = max(per, lno - cur)
    return [sup, per]


def conditionalTransactions(patterns, timestamp):
    """
    To sort and update the conditional transactions by removing the items which fails frequency
    and periodicity conditions

    :param patterns: conditional patterns of a node
    :param timestamp: timeStamps of a conditional pattern
    :return: conditional transactions with their respective timeStamps
    """
    pat = []
    timeStamps = []
    data1 = {}
    for i in range(len(patterns)):
        for j in patterns[i]:
            if j in data1:
                data1[j] = merge(data1[j], timestamp[i])
            else:
                data1[j] = timestamp[i]

    updatedDict = {}
    for m in data1:
        updatedDict[m] = getPeriodAndSupport(data1[m])
    updatedDict = {k: v for k, v in updatedDict.items() if v[0] >= minSup and v[1] <= maxPer}
    count = 0
    for p in patterns:
        p1 = [v for v in p if v in updatedDict]
        trans = sorted(p1, key=lambda x: (updatedDict.get(x)[0], -x), reverse=True)
        if len(trans) > 0:
            pat.append(trans)
            timeStamps.append(timestamp[count])
        count += 1
    return pat, timeStamps, updatedDict


class PSGrowth(periodicFrequentPatterns):
    """PS-Growth is one of the fundamental algorithm to discover periodic-frequent patterns in a temporal database.

        Reference :
        ----------
        A. Anirudh, R. U. Kiran, P. K. Reddy and M. Kitsuregaway, "Memory efficient mining of periodic-frequent
        patterns in transactional databases," 2016 IEEE Symposium Series on Computational Intelligence (SSCI),
        2016, pp. 1-8, https://doi.org/10.1109/SSCI.2016.7849926
        
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
            it represents the total no of transaction
        tree : class
            it represents the Tree class
        itemSetCount : int
            it represents the total no of patterns
        finalPatterns : dict
            it represents to store the patterns

        Methods
        -------
            startMine()
                Mining process will start from here
            getFrequentPatterns()
                Complete set of patterns will be retrieved with this function
            storePatternsInFile(oFile)
                Complete set of periodic-frequent patterns will be loaded in to a output file
            getConditionalPatternsInDataFrame()
                Complete set of periodic-frequent patterns will be loaded in to a dataframe
            getMemoryUSS()
                Total amount of USS memory consumed by the mining process will be retrieved from this function
            getMemoryRSS()
                Total amount of RSS memory consumed by the mining process will be retrieved from this function
            getRuntime()
                Total amount of runtime taken by the mining process will be retrieved from this function
            creatingItemSets()
                Scans the dataset or dataframes and stores in list format
            buildTree()
                after updating the Databases ar added into the tree by setting root node as null
            startMine()
                the main method to run the program

        Executing the code on terminal:
        -------
        Format:
        ------
        python3 PSGrowth.py <inputFile> <outputFile> <minSup> <maxPer>

        Examples:
        --------
        python3 PSGrowth.py sampleTDB.txt patterns.txt 0.3 0.4   (minSup and maxPer will be considered in percentage of database
        transactions)

        python3 PSGrowth.py sampleTDB.txt patterns.txt 3 4     (minSup and maxPer will be considered in support count or frequency)
        
        
        Sample run of the imported code:
        --------------
        from PAMI.periodicFrequentPattern.basic import PSGrowth as alg

        obj = alg.PSGrowth("../basic/sampleTDB.txt", "2", "6")

        obj.startMine()

        periodicFrequentPatterns = obj.getPeriodicFrequentPatterns()

        print("Total number of Frequent Patterns:", len(periodicFrequentPatterns))

        obj.storePatternsInFile("patterns")

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

    startTime = float()
    endTime = float()
    minSup = str()
    maxPer = float()
    finalPatterns = {}
    iFile = " "
    oFile = " "
    memoryUSS = float()
    memoryRSS = float()
    Database = []
    rank = {}
    lno = 0

    def convert(self, value):
        """
        To convert the given user specified value

        :param value: user specified value
        :return: converted value
        """
        if type(value) is int:
            value = int(value)
        if type(value) is float:
            value = (self.lno * value)
        if type(value) is str:
            if '.' in value:
                value = float(value)
                value = (self.lno * value)
            else:
                value = int(value)
        return value

    def creatingItemSets(self):
        """
            Storing the complete values of a database/input file into a database variable



        """
        global minSup, maxPer, lno
        data = {}
        with open(self.iFile, 'r') as f:
            for line in f:
                self.lno += 1
                tr = [i.rstrip() for i in line.split("\t")]
                for i in range(1, len(tr)):
                    if tr[i] not in data:
                        data[tr[i]] = [int(tr[0]), int(tr[0]), 1]
                    else:
                        data[tr[i]][0] = max(data[tr[i]][0], (int(tr[0]) - data[tr[i]][1]))
                        data[tr[i]][1] = int(tr[0])
                        data[tr[i]][2] += 1
        for key in data:
            data[key][0] = max(data[key][0], self.lno - data[key][1])
        self.minSup = self.convert(self.minSup)
        self.maxPer = self.convert(self.maxPer)
        minSup, maxPer, lno = self.minSup, self.maxPer, self.lno
        data = {k: [v[2], v[0]] for k, v in data.items() if v[0] <= self.maxPer and v[2] >= self.minSup}
        genList = [k for k, v in sorted(data.items(), key=lambda x: (x[1][0], x[0]), reverse=True)]
        self.rank = dict([(index, item) for (item, index) in enumerate(genList)])
        return data, genList

    def buildTree(self, info, sampleDict):
        """ it takes the Databases and support of each item and construct the main tree with setting root
                            node as null

            :param info: it represents the support of each item
            :type info: dictionary
            :param sampleDict: One length periodic-frequent patterns in a dictionary
            :type sampleDict: dict
            :return: Returns the root node of the tree
        """
        rootNode = Tree()
        rootNode.info = info.copy()
        k = 0
        with open(self.iFile, 'r') as f:
            for line in f:
                k += 1
                tr = [i.rstrip() for i in line.split("\t")]
                list2 = [int(tr[0])]
                for i in range(1, len(tr)):
                    if tr[i] in sampleDict:
                        list2.append(self.rank[tr[i]])
                if len(list2) >= 2:
                    basket = list2[1:]
                    basket.sort()
                    list2[1:] = basket[0:]
                    rootNode.addTransaction(list2[1:], list2[0])
        return rootNode

    def startMine(self):
        """
            Mining process will start from this function
        """
        global minSup, maxPer, lno, pfList
        self.startTime = time.time()
        if self.iFile is None:
            raise Exception("Please enter the file path or file name:")
        if self.minSup is None:
            raise Exception("Please enter the Minimum Support")
        OneLengthPeriodicItems, pfList = self.creatingItemSets()
        info = {self.rank[k]: v for k, v in OneLengthPeriodicItems.items()}
        Tree = self.buildTree(info, OneLengthPeriodicItems)
        patterns = Tree.generatePatterns([])
        for i in patterns:
            sample = str()
            for k in i[0]:
                sample = sample + k + " "
            self.finalPatterns[sample] = i[1]
        self.endTime = time.time()
        process = psutil.Process(os.getpid())
        self.memoryUSS = process.memory_full_info().uss
        self.memoryRSS = process.memory_info().rss
        print("Periodic-Frequent patterns were generated successfully using PS-Growth algorithm ")

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
        """Storing final periodic-frequent patterns in a dataframe

        :return: returning periodic-frequent patterns in a dataframe
        :rtype: pd.DataFrame
        """

        dataFrame = {}
        data = []
        for a, b in self.finalPatterns.items():
            data.append([a, b[0], b[1]])
            dataFrame = pd.DataFrame(data, columns=['Patterns', 'Support', 'Periodicity'])
        return dataFrame

    def storePatternsInFile(self, outFile):
        """Complete set of periodic-frequent patterns will be loaded in to a output file

        :param outFile: name of the output file
        :type outFile: file
        """
        self.oFile = outFile
        writer = open(self.oFile, 'w+')
        for x, y in self.finalPatterns.items():
            s1 = x + ":" + str(y[0]) + ":" + str(y[1])
            writer.write("%s \n" % s1)

    def getPeriodicFrequentPatterns(self):
        """ Function to send the set of periodic-frequent patterns after completion of the mining process

        :return: returning periodic-frequent patterns
        :rtype: dict
        """
        return self.finalPatterns


if __name__ == "__main__":
    if len(sys.argv) == 5:
        ap = PSGrowth(sys.argv[1], sys.argv[3], sys.argv[4])
        ap.startMine()
        frequentPatterns = ap.getPeriodicFrequentPatterns()
        print("Total number of periodic-frequent patterns:", len(frequentPatterns))
        ap.storePatternsInFile(sys.argv[2])
        memUSS = ap.getMemoryUSS()
        print("Total Memory in USS:", memUSS)
        memRSS = ap.getMemoryRSS()
        print("Total Memory in RSS", memRSS)
        run = ap.getRuntime()
        print("Total ExecutionTime in seconds:", run)
    else:
        print("Error! The number of input parameters do not match the total number of parameters provided")
