import sys
import pandas as pd
from abstract import *
class Element:
    """
    A class represents an Element of a utility list as used by the HDSHUI algorithm.

        Attributes
        ----------
        tid : int
            keep tact of transaction id
        nu : int
            non closed itemset utility
        nru : int
             non closed remaining utility
        pu : int
            prefix utility
        ppos: int
            position of previous item in the list
    """

    def __init__(self,tid,nu,nru,pu,ppos):
        self.tid=tid
        self.nu=nu
        self.nru=nru
        self.pu=pu
        self.ppos=ppos
class CUList:
    """
        A class represents a UtilityList as used by the HDSHUI algorithm.

        Attributes
        ----------
        item: int
            item 
        sumNu: long
            the sum of item utilities
        sumNru: long
            the sum of remaining utilities
        sumCu : long
            the sum of closed utilities
        sumCru: long
            the sum of closed remaining utilities
        sumCpu: long
            the sum of closed prefix utilities
        elements: list
            the list of elements 

        Methods
        -------
        addElement(element)
            Method to add an element to this utility list and update the sums at the same time.

    """
    def __init__(self,item):
        self.item=item
        self.sumnu = 0
        self.sumnru = 0
        self.sumCu = 0
        self.sumCru = 0
        self.sumCpu = 0
        self.elements=[]
    def addElements(self,element):
        """
            A method to add new element to CUList
            :param element: element to be addeed to CUList
            :type element: Element
        """
        self.sumnu+=element.nu
        self.sumnru+=element.nru
        self.elements.append(element)

class Pair:
    """
        A class represent an item and its utility in a transaction
    """
    def __init__(self):
        self.item=0
        self.utility=0

class SHDSHUIs(utilityPatterns):
    """
        Spatial High Utility Itemset Mining (SHUIM) [3] is an important model in data
        mining with many real-world applications. It involves finding all spatially interesting itemsets having high value 
        in a quantitative spatiotemporal database.

        Parameters
        ----------
        self.iFile : file
            Name of the input file to mine complete set of frequent patterns
       self. oFile : file
            Name of the output file to store complete set of frequent patterns
        memoryRSS : float
            To store the total amount of RSS memory consumed by the program
        startTime:float
            To record the start time of the mining process
        endTime:float
            To record the completion time of the mining process
        minUtil : int
            The user given minUtil
        mapFMAP: list
            EUCS map of the FHM algorithm
        candidates: int
            candidates genetated
        huiCnt: int
            huis created
        neighbors: map
            keep track of nighboues of elements
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

        Executing the code on terminal
        -------
        Format: python3 HDSHUIM.py <inputFile> <outputFile> <Neighbours> <minUtil>
        Examples: python3 HDSHUIM.py sampleTDB.txt output.txt sampleN.txt 35 
        
        Sample run of importing the code:
        -------------------------------
        
        import HDSHUIM as alg

        obj=alg.SHDSHUIs("sampleTDB.txt","sampleN.txt",35)

        obj.startMine()

        frequentPatterns = obj.getUtilityPatterns()

        print("Total number of Spatial Frequent Patterns:", len(frequentPatterns))

        obj.storePatternsInFile("output")

        memUSS = obj.getMemoryUSS()

        print("Total Memory in USS:", memUSS)

        memRSS = obj.getMemoryRSS()

        print("Total Memory in RSS", memRSS)

        run = obj.getRuntime()

        print("Total ExecutionTime in seconds:", run)

        Credits:
        -------
            The complete program was written by Sai Chitra.B under the supervision of Professor Rage Uday Kiran.

    """
    
    startTime = float()
    endTime = float()
    minSup = str()
    maxPer = float()
    finalPatterns = {}
    iFile = " "
    oFile = " "
    minUtil=0
    memoryUSS = float()
    memoryRSS = float()
    def __init__(self,iFile1,neighb1,minUtil):
        super().__init__(iFile1,neighb1,minUtil)
        self.startTime=0
        self.endTime=0
        self.hui_cnt=0
        self.candidates=0
        self.mapOfPMU={}
        self.mapFMAP={}
        self.neighbors={}
        self.finalPatterns = {}
    def compareItems(self,o1,o2):
        """
            A method to sort  list of huis in pmu asending order
        """
        compare=self.mapOfPMU[o1.item]-self.mapOfPMU[o2.item]
        if compare==0:
            return int(o1.item)-int(o2.item)
        else:
            return compare
    def startMine(self):
        """main program to start the operation
        """
        minUtil=self.minUtil
        self.startTime=datetime.datetime.now()
        with open(self.nFile,'r') as file1:
            for line in file1:
                parts=line.split()
                item=parts[0]
                neigh1=set()
                for i in range(1,len(parts)):
                    neigh1.add(parts[i])
                self.neighbors[item]=neigh1
        with open(self.iFile,'r') as file:
            for line in file:
                parts=line.split(":")
                items_str=parts[0].split()
                utility_str=parts[2].split()
                transUtility=int(parts[1])
                trans1=set()
                for i in range(0,len(items_str)):
                    trans1.add(items_str[i])
                for i in range(0,len(items_str)):
                    item=items_str[i]
                    twu=self.mapOfPMU.get(item)
                    if(twu==None):
                        twu=int(utility_str[i])
                    else:
                        twu+=int(utility_str[i])
                    self.mapOfPMU[item]=twu
                    if(self.neighbors.get(item)==None):
                        continue
                    neighbours2=trans1.intersection(self.neighbors.get(item))    
                    for item2 in neighbours2:
                        if(self.mapOfPMU.get(item2)==None):
                            self.mapOfPMU[item2]=int(utility_str[i])
                        else:
                            self.mapOfPMU[item2]+=int(utility_str[i])

        listOfCUList=[]
        hashTable={}
        mapItemsToCUList={}
        for item in self.mapOfPMU.keys():
            if(self.mapOfPMU.get(item)>=minUtil):
                uList=CUList(item)
                mapItemsToCUList[item]=uList
                listOfCUList.append(uList)
        listOfCUList.sort(key=functools.cmp_to_key(self.compareItems))
        tid=1
        with open(self.iFile,'r') as file:
            for line in file:
                parts=line.split(":")
                items=parts[0].split()
                utilities=parts[2].split()
                ru=0
                newTwu=0
                tx_key=[]
                revisedTrans=[]
                for i in range(0,len(items)):
                    pair=Pair()
                    pair.item=items[i]
                    pair.utility=int(utilities[i])
                    if(self.mapOfPMU.get(pair.item)>=minUtil):
                        revisedTrans.append(pair)
                        tx_key.append(pair.item)
                        newTwu+=pair.utility
                revisedTrans.sort(key=functools.cmp_to_key(self.compareItems))
                tx_key1=tuple(tx_key)
                if(len(revisedTrans)>0):
                    if tx_key1 not in hashTable.keys():
                        hashTable[tx_key1]=len(mapItemsToCUList[revisedTrans[len(revisedTrans)-1].item].elements)
                        for i in range(len(revisedTrans)-1,-1,-1):
                            pair=revisedTrans[i]
                            cuListoFItems=mapItemsToCUList.get(pair.item)
                            element=Element(tid,pair.utility,ru,0,0)
                            if(i>0):
                                element.ppos=len(mapItemsToCUList[revisedTrans[i-1].item].elements)
                            else:
                                element.ppos=-1
                            cuListoFItems.addElements(element)
                            ru+=pair.utility
                    else:
                        pos=hashTable[tx_key1]
                        ru=0
                        for i in range(len(revisedTrans)-1,-1,-1):
                            cuListoFItems=mapItemsToCUList[revisedTrans[i].item]
                            cuListoFItems.elements[pos].nu+=revisedTrans[i].utility
                            cuListoFItems.elements[pos].nru+=ru
                            cuListoFItems.sumnu+=revisedTrans[i].utility
                            cuListoFItems.sumnru+=ru
                            ru+=revisedTrans[i].utility
                            pos=cuListoFItems.elements[pos].ppos
                #EUCS
                for i in range(len(revisedTrans)-1,-1,-1):
                    pair=revisedTrans[i]
                    mapFMAPItem=self.mapFMAP.get(pair.item)
                    if(mapFMAPItem==None):
                        mapFMAPItem={}
                        self.mapFMAP[pair.item]=mapFMAPItem
                    for j in range(i+1,len(revisedTrans)):
                        pairAfter=revisedTrans[j]
                        twuSUm=mapFMAPItem.get(pairAfter.item)
                        if(twuSUm==None):
                            mapFMAPItem[pairAfter.item]=newTwu
                        else:
                            mapFMAPItem[pairAfter.item]=twuSUm+newTwu
                tid+=1
        ExNeighbors=set(self.mapOfPMU.keys())
        self.Explore_SearchTree([],listOfCUList,ExNeighbors,minUtil)
        self.endTime=datetime.datetime.now()
        process = psutil.Process(os.getpid())
        self.memoryUSS = process.memory_full_info().uss
        self.memoryRSS = process.memory_info().rss
    def Explore_SearchTree(self,prefix,uList,ExNeighbors,minUtil):
        """
            A method to find all high utility itemsets

           Attributes
            -----------
            :parm prefix: it represent all items in prefix
            :type prefix :list
            :parm uList:projectd Utility list
            :type uList: list
            :parm ExNeighbors: keep track of common nighbours
            :type ExNeighbors: set
            :parm minUtil:user minUtil
            :type minUtil:int
        """
        for i in range(0,len(uList)):
            x=uList[i]
            if not x.item in ExNeighbors:
                continue
            self.candidates+=1
            soted_prefix=[0]*(len(prefix)+1)
            soted_prefix=prefix[0:len(prefix)+1]
            soted_prefix.append(x.item)
            if (x.sumnu + x.sumCu >= minUtil) and(x.item in ExNeighbors):
                self.saveItemset(prefix,len(prefix),x.item,x.sumnu+x.sumCu)
            if x.sumnu+x.sumCu+x.sumnru+x.sumCru>=minUtil:#U-Prune # and (x.item in ExNeighbors)):
                ULIST=[]
                for j in range(i,len(uList)):
                    if (uList[j].item in ExNeighbors) and (self.neighbors.get(x.item) != None) and (uList[j].item in self.neighbors.get(x.item)):
                        ULIST.append(uList[j])        
                exULs=self.construcCUL(x,ULIST,-1,minUtil,len(soted_prefix),ExNeighbors)
                if self.neighbors.get(x.item)!=None and ExNeighbors!=None:
                    set1=ExNeighbors.intersection(self.neighbors.get(x.item))
                    if exULs==None or set1==None:
                        continue
                    self.Explore_SearchTree(soted_prefix,exULs,set1,minUtil)

    def construcCUL(self,x,culs,st,minUtil,length,exnighbors):
        """
            A method to construct CUL's database

           Attributes
            -----------
            :parm x: Compact utility list
            :type x: list
            :parm culs:list of Compact utility lists
            :type culs:list
            :parm st: starting pos of culs
            :type st:int
            :parm minUtil: user minUtil
            :type minUtil:int
            :parm length: length of x
            :type length:int
            :parm exnighbors: common nighbours
            :type exnighbors: list
            :return: projectd database of list X
            :rtype: list
        """
        excul=[]
        lau=[]
        cutil=[]
        ey_tid=[]
        for i in range(0,len(culs)):
            uList=CUList(culs[i].item)
            excul.append(uList)
            lau.append(0)
            cutil.append(0)
            ey_tid.append(0)
        sz=len(culs)-(st+1)
        exSZ=sz
        for j in range(st+1,len(culs)):
            mapOfTWUF=self.mapFMAP[x.item]
            if(mapOfTWUF!=None):
                twuf=mapOfTWUF.get(culs[j].item)
                if twuf!=None and twuf<minUtil or (not (excul[j].item in exnighbors)):
                    excul[j]=None
                    exSZ=sz-1
                else:
                    uList=CUList(culs[j].item)
                    excul[j]=uList
                    ey_tid[j]=0
                    lau[j]=x.sumCu+x.sumCru+x.sumnu+x.sumnru
                    cutil[j]=x.sumCu+x.sumCru
        hashTable={}            
        for ex in x.elements:
            newT=[]
            for j in range(st+1,len(culs)):
                if excul[j]==None:
                    continue
                eylist=culs[j].elements
                while ey_tid[j]<len(eylist) and eylist[ey_tid[j]].tid<ex.tid:
                    ey_tid[j]=ey_tid[j]+1
                if ey_tid[j]<len(eylist) and eylist[ey_tid[j]].tid==ex.tid:
                    newT.append(j)
                else:
                    lau[j]=lau[j]-ex.nu-ex.nru
                    if lau[j]<minUtil:
                        excul[j]=None
                        exSZ=exSZ-1
            if len(newT)==exSZ:
                self.UpdateCLosed(x,culs,st,excul,newT,ex,ey_tid,length)
            else:
                if len(newT)==0:
                    continue
                ru=0
                newT1=tuple(newT)
                if newT1 not in hashTable.keys():
                    hashTable[newT1]=len(excul[newT[len(newT)-1]].elements)
                    for i in range(len(newT)-1,-1,-1):
                        cuListoFItems=excul[newT[i]]
                        y=culs[newT[i]].elements[ey_tid[newT[i]]]
                        element=Element(ex.tid,ex.nu+y.nu-ex.pu,ru,ex.nu,0)
                        if(i>0):
                            element.ppos=len(excul[newT[i-1]].elements)
                        else:
                            element.ppos=-1
                        cuListoFItems.addElements(element)
                        ru+=y.nu-ex.pu
                else:
                    dppos=hashTable[newT1]
                    self.updateElement(x,culs,st,excul,newT,ex,dppos,ey_tid)
            for j in range(st+1,len(culs)):
                cutil[j]=cutil[j]+ex.nu+ex.nru
        filter_culs=[]
        for j in range(st+1,len(culs)):
            if cutil[j]<minUtil or excul[j]==None:
                continue
            else:
                if length>1:
                    excul[j].sumCu+=culs[j].sumCu+x.sumCu-x.sumCpu
                    excul[j].sumCru+=culs[j].sumCru
                    excul[j].sumCpu+=x.sumCu
                filter_culs.append(excul[j])
        return filter_culs
    
    def UpdateCLosed(self,x,culs,st,excul,newT,ex,ey_tid,length):
        """
            A method to update closed values
           Attributes
            -----------
            :parm x: Compact utility list
            :type x: list
            :parm culs:list of Compact utility lists
            :type culs:list
            :parm st: starting pos of culs
            :type st:int
            :parm newT:transaction to be updated
            :type newT:list
            :parm ex: element ex
            :type ex:element
            :parm ey_tid:list of tids
            :type ey_tid:tid
            :parm length: length of x
            :type length:int

        """
        nru=0
        for j in range(len(newT)-1,-1,-1):
            ey=culs[newT[j]]
            eyy=ey.elements[ey_tid[newT[j]]]
            excul[newT[j]].sumCu+=ex.nu+eyy.nu-ex.pu
            excul[newT[j]].sumCru+=nru
            excul[newT[j]].sumCpu+=ex.nu
            nru=nru+eyy.nu-ex.pu

    def updateElement(self,z,culs,st,excul,newT,ex,duppos,ey_tid):
        """
            A method to updates vales for duplicates

           Attributes
            -----------
            :parm z: Compact utility list
            :type z: list
            :parm culs:list of Compact utility lists
            :type culs:list
            :parm st: starting pos of culs
            :type st:int
            :parm excul:list of culs
            :type excul:list
            :parm newT:transaction to be updated
            :type newT:list
            :parm ex: element ex
            :type ex:element
            :parm duppos: position of z in excul
            :type duppos:int
            :parm ey_tid:list of tids
            :type ey_tid:tid
        """
        nru=0
        pos=duppos
        for j in range(len(newT)-1,-1,-1):
            ey=culs[newT[j]]
            eyy=ey.elements[ey_tid[newT[j]]]
            excul[newT[j]].elements[pos].nu+=ex.nu+eyy.nu-ex.pu
            excul[newT[j]].sumnu+=ex.nu+eyy.nu-ex.pu
            excul[newT[j]].elements[pos].nru+=nru
            excul[newT[j]].sumnru+=nru
            excul[newT[j]].elements[pos].pu+=ex.nu
            nru=nru+eyy.nu-ex.pu
            pos=excul[newT[j]].elements[pos].ppos
            
    def saveItemset(self,prefix,prefixlen,item,utility):
        """
         A method to save itemsets

        Attributes
        -----------
        :parm prefix: it represent all items in prefix
        :type prefix :list
        :pram prefixLen: length of prefix
        :type prefixLen:int
        :parm item:item
        :type item: int
        :parm utility:utlity of itemset
        :type utility:int
        """
        self.hui_cnt+=1
        res=""
        for i in range(0,prefixlen):
            res+=str(prefix[i])+" "
        res+=str(item)
        res1=str(utility)+"\n"
        self.finalPatterns[res]=res1
        #self.bwriter.write(res)

    def getPatternsInDataFrame(self):
        """Storing final frequent patterns in a dataframe

        :return: returning frequent patterns in a dataframe
        :rtype: pd.DataFrame
        """

        dataFrame = {}
        data = []
        for a, b in self.finalPatterns.items():
            data.append([a, b])
            dataFrame = pd.DataFrame(data, columns=['Patterns', 'Support'])
        return dataFrame
    def getUtilityPatterns(self):
        """ Function to send the set of frequent patterns after completion of the mining process

        :return: returning frequent patterns
        :rtype: dict
        """
        return self.finalPatterns
    def storePatternsInFile(self, outFile):
        """Complete set of frequent patterns will be loaded in to a output file

        :param outFile: name of the output file
        :type outFile: file
        """
        self.oFile = outFile
        writer = open(self.oFile, 'w+')
        for x, y in self.finalPatterns.items():
            patternsAndSupport = str(x) + " : " + str(y)
            writer.write("%s \n" % patternsAndSupport)
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
        dif=self.endTime-self.startTime
        return dif.total_seconds()*1000
if __name__ == "__main__":
    if len(sys.argv)==5:
        ap=SHDSHUIs(sys.argv[1],sys.argv[3],int(sys.argv[4]))
        ap.startMine()
        frequentPatterns = ap.getUtilityPatterns()
        print("Total number of Spatial Frequent Patterns:", len(frequentPatterns))
        ap.storePatternsInFile(sys.argv[2])
        memUSS = ap.getMemoryUSS()
        print("Total Memory in USS:", memUSS)
        memRSS = ap.getMemoryRSS()
        print("Total Memory in RSS", memRSS)
        run = ap.getRuntime()
        print("Total ExecutionTime in seconds:", run)
    else:
         print("Error! The number of input parameters do not match the total number of parameters provided")
