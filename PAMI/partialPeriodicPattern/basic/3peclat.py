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
from abstract import *


class ThreePEclat(partialPeriodicPatterns):
    """ 3pEclat is the fundamental approach to mine the partial periodic frequent patterns.

        Reference :

        Parameters
        ----------
        self.iFile : file
            Name of the Input file to mine complete set of frequent patterns
       self. oFile : file
            Name of the output file to store complete set of frequent patterns
        memoryUSS : float
            To store the total amount of USS memory consumed by the program
        memoryRSS : float
            To store the total amount of RSS memory consumed by the program
        startTime:float
            To record the start time of the mining process
        endTime:float
            To record the completion time of the mining process
        periodicSupport : int/float
            The user given minimum support
        period : int/float
            The user specified maximum period
        Database : list
            To store the transactions of a database in list
        mapSupport : Dictionary
            To maintain the information of item and their frequency
        lno : int
            it represents the total no of transactions
        tree : class
            it represents the Tree class
        itemSetCount : int
            it represents the total no of patterns
        finalPatterns : dict
            it represents to store the patterns
        tidList : dict
            stores the timestamps of an item
        hashing : dict
            stores the patterns with their support to check for the closed property

        Methods
        -------
        startMine()
            Mining process will start from here
        getFrequentPatterns()
            Complete set of patterns will be retrieved with this function
        storePatternsInFile(oFile)
            Complete set of frequent patterns will be loaded in to a output file
        getPatternsInDataFrame()
            Complete set of frequent patterns will be loaded in to a dataframe
        getMemoryUSS()
            Total amount of USS memory consumed by the mining process will be retrieved from this function
        getMemoryRSS()
            Total amount of RSS memory consumed by the mining process will be retrieved from this function
        getRuntime()
            Total amount of runtime taken by the mining process will be retrieved from this function
        creatingOneitemSets()
            Scan the database and store the items with their timestamps which are periodic frequent 
        getPeriodAndSupport()
            Calculates the support and period for a list of timestamps.
        Generation()
            Used to implement prefix class equivalence method to generate the periodic patterns recursively
        startMine()
            Main program
        Executing the code on terminal
        -------
        Format: python3 3peclat.py <inputFile> <outputFile> <periodicSupport>
        Examples: python3 3peclat.py sampleDB.txt patterns.txt 0.3 0.4   (periodicSupport will be considered in percentage of database transactions)
                  python3 3peclat.py sampleDB.txt patterns.txt 3 4     (periodicSupport will be considered in support count or frequency)
        
        Sample run of importing the code:
        -------------------
         
        from PAMI.periodicFrequentPattern.basic import 3peclat as alg

        obj = alg.ThreePEclat(iFile, periodicSupport,period)

        obj.startMine()

        partialPeriodicPatterns = obj.getPartialPeriodicPatterns()

        print("Total number of partial periodic patterns:", len(partialPeriodicPatterns))

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
    startTime = float()
    endTime = float()
    finalPatterns = {}
    iFile = " "
    oFile = " "
    memoryUSS = float()
    memoryRSS = float()
    mapSupport = {}
    hashing = {}
    itemsetCount = 0
    writer = None
    periodicSupport = str()
    period = str()
    tidList = {}
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
            value = (len(self.Database) * value)
        if type(value) is str:
            if '.' in value:
                value = float(value)
                value = (len(self.Database) * value)
            else:
                value = int(value)
        return value


    def getPeriodicSupport(self, tids):
        """
            calculates the support and periodicity with list of timestamps

            :param tids : timestamps of a pattern
            :type tids : list


                    """
        tids.sort()
        sup = 0
        for j in range(len(tids) - 1):
            per = abs(tids[j+1] - tids[j])
            if per <= self.period:
                sup += 1
        return sup

    def creatingOneitemSets(self):
        """
                    Storing the complete transactions of the database/input file in a database variable


                    """
        self.lno = len(open(self.iFile).readlines())
        self.period = self.convert(self.period)
        with open(self.iFile, 'r') as f:
            for line in f:
                s = [i.strip() for i in line.split("\t")]
                n = int(s[0])
                for i in range(1, len(s)):
                    si = s[i]
                    if self.mapSupport.get(si) is None:
                        self.mapSupport[si] = [0, n]
                        self.tidList[si] = [n]
                    else:
                        lp = n - self.mapSupport[si][1]
                        if lp <= self.period:
                            self.mapSupport[si][0] += 1
                        self.mapSupport[si][1] = n
                        self.tidList[si].append(n)
        self.periodicSupport = self.convert(self.periodicSupport)
        self.mapSupport = {k: v[0] for k, v in self.mapSupport.items() if v[0] >= self.periodicSupport}
        plist = [key for key, value in sorted(self.mapSupport.items(), key=lambda x:x[1], reverse=True)]
        return plist
    
    def save(self, prefix, suffix, tidSetX):
        """
            saves the patterns that satisfy the periodic frequent property.

            :param prefix: the prefix of a pattern
            :type prefix: list
            :param suffix : the suffix of a patterns
            :type suffix : list
            :param tidSetX : the timestamp of a patterns
            :type tidSetX : list


                    """
        if prefix is None:
            prefix = suffix
        else:
            prefix = prefix + suffix
        val = self.getPeriodicSupport(tidSetX)
        if val >= self.periodicSupport:
            sample = str()
            for i in prefix:
                sample = sample + i + " "
            self.finalPatterns[sample] = val
    
    def Generation(self, prefix, itemSets, tidSets):
        """
            here equivalence class is followed  and checks for the patterns generated for periodic frequent patterns.

            :param prefix :  main equivalence prefix
            :type prefix : periodic-frequent item or pattern
            :param itemSets : patterns which are items combined with prefix and satisfying the periodicity
                            and frequent with their timestamps
            :type itemSets : list
            :param tidSets : timestamps of the items in the argument itemSets
            :type tidSets : list


                    """
        if len(itemSets) == 1:
            i = itemSets[0]
            tidi = tidSets[0]
            self.save(prefix, [i], tidi)
            return
        for i in range(len(itemSets)):
            itemI = itemSets[i]
            if itemI == None:
                continue
            tidSetX = tidSets[i]
            classItemSets = []
            classTidSets = []
            itemSetX = [itemI]
            for j in range(i+1, len(itemSets)):
                itemJ = itemSets[j]
                tidSetJ = tidSets[j]
                y = list(set(tidSetX).intersection(tidSetJ))
                val = self.getPeriodicSupport(y)
                if val >= self.periodicSupport:
                    classItemSets.append(itemJ)
                    classTidSets.append(y)
            newprefix = list(set(itemSetX)) + prefix
            self.Generation(newprefix, classItemSets, classTidSets)
            self.save(prefix, list(set(itemSetX)), tidSetX)
        
    def startMine(self):
        """
                Main program start with extracting the periodic frequent items from the database and
                performs prefix equivalence to form the combinations and generates closed periodic frequent patterns.


                    """
        self.startTime = time.time()
        plist = self.creatingOneitemSets()
        for i in range(len(plist)):
            itemI = plist[i]
            tidSetX = self.tidList[itemI]
            itemSetX = [itemI]
            itemSets = []
            tidSets = []
            for j in range(i+1, len(plist)):
                itemJ = plist[j]
                tidSetJ = self.tidList[itemJ]
                y1 = list(set(tidSetX).intersection(tidSetJ))
                val = self.getPeriodicSupport(y1)
                if val >= self.periodicSupport:
                    itemSets.append(itemJ)
                    tidSets.append(y1)
            self.Generation(itemSetX, itemSets, tidSets)
            self.save(None, itemSetX, tidSetX)
        print("Partial Periodic Frequent patterns were generated successfully using 3peclat algorithm")
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

    def getPartialPeriodicPatterns(self):
        """ Function to send the set of frequent patterns after completion of the mining process

        :return: returning frequent patterns
        :rtype: dict
        """
        return self.finalPatterns
                    

if __name__ == "__main__":
    if len(sys.argv) == 5:
        ap = ThreePEclat(sys.argv[1], sys.argv[3], sys.argv[4])
        ap.startMine()
        frequentPatterns = ap.getPartialPeriodicPatterns()
        print("Total number of Frequent Patterns:", len(frequentPatterns))
        ap.storePatternsInFile(sys.argv[2])
        memUSS = ap.getMemoryUSS()
        print("Total Memory in USS:", memUSS)
        memRSS = ap.getMemoryRSS()
        print("Total Memory in RSS", memRSS)
        run = ap.getRuntime()
        print("Total ExecutionTime in seconds:", run)
    else:
        print("Error! The number of input parameters do not match the total number of parameters provided")
