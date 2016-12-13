import os, csv, fnmatch
import time
import sys
import re
import setlr30 as setlr
from time import sleep
#==============================================================================
def getFileTypes(fileName):
    if '.png' in fileName or '.jpg' in fileName:
        fileType = 'Image'
    elif '.csv' in fileName:
        fileType = 'CSV'
    elif '.xls' in fileName or '.xlsx' in fileName:
        fileType = 'Excel'
    elif '.txt' in fileName:
        fileType = 'Text'
    else:
        fileType = 'Unidentified'
    return fileType

def getFullFilePath(imFileList, dirName):
    fullFilePath = []
    for fileName in fnmatch.filter(imFileList, '*.*'):
        fullFilePath.append(os.path.join(dirName, fileName))
    return fullFilePath
    
def getCouponName(fileName):
    regex = re.compile("[0-9]{0,}[\\-_][0-9]{0,}[\\-_][0-9]{0,}")
    matchArray = regex.findall(fileName)
    if(matchArray):
        return matchArray[0].replace('_', '-')
    else:
        return ''
        
def getImageAttributes(fileName):
    if '.png' in fileName or '.jpg' in fileName:
        name = fileName.split('.')[0]
        nameTypes = name.split('-')
        series = nameTypes[0]
        panel = nameTypes[1]
        coupon = nameTypes[2]
        attributes = [series, panel, coupon]
        return attributes
    else:
        return []
        
def getSeries(dirName):
    if 'DOE_I/' in dirName or 'DOE_I_' in dirName:
        return 'Series 2'
    elif 'DOE_II/' in dirName or 'DOE_II_' in dirName:
        return 'Series 6'
    elif 'DOE_IV/' in dirName or 'DOE_IV_' in dirName:
        return 'Series 10'

def setNamesOfFilesinParamsTTl(pathOfParamTTl, nameOfParamTTl, nameOfCSV, nameOfResultTTl):
    regexCSV = re.compile("^[ \t]*[p][r][o][v][:]+[0-9A-Za-z ]+[<]+[0-9A-Za-z]+[.][0-9A-Za-z]+[>][ ]*[;]")
    regexTTL = re.compile("^[ \t]*[<][ 0-9A-Za-z]+[.][t][t][l][>][ ]*[a][ ]*[p][v][:][0-9A-Za-z ]+[;]")
    replacementStringCSV = "prov:used <"+nameOfCSV+">;"
    replacementStringTTL = "<"+nameOfResultTTl+"> a pv:File;"
    results = os.path.join(os.path.dirname(__file__), "Results", nameOfParamTTl)
    fp = open(pathOfParamTTl, "r")
    lines = fp.readlines()
    toWrite = ''
    l = []
    for line in lines:
        try:
            matchArrayCSV = regexCSV.findall(line.strip())
            if(matchArrayCSV[0] in line):
                line = replacementStringCSV
        except:
            pass
        try:
            matchArrayTTL = regexTTL.findall(line.strip())
            if(matchArrayTTL[0] in line):
                line = replacementStringTTL
        except:
            pass
        toWrite = toWrite.rstrip() + line.rstrip()
        l.append(line.rstrip())
        l.append("\n")
    fp.close()
    fp = open(results, "w+")
    for i in l:
        fp.write(i)
    fp.close()

#==============================================================================



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error in arguments passed.\nStandard input format:")
        print("$python3 <filename> <directorypath>")
        sys.exit()
        
    current_file_dir = os.path.dirname(__file__)
    results = os.path.join(current_file_dir, "Results")
    os.makedirs(results, exist_ok=True)
    datetime = time.strftime("%Y%m%d_%H%M%S")
    #nameOfCSV = 'graphFilePath_run_'+datetime+'.csv'
    #nameOfDirectoryCSV = 'graphDirectory_run_'+datetime+'.csv'
    nameOfDirectoryCSV = 'graphDirectory.csv'
    archiveCSV_file_path = os.path.join(current_file_dir, "Results", nameOfDirectoryCSV)
    nameOfInstanceCSV = 'graphFilePath.csv'
    instanceCSV_file_path = os.path.join(current_file_dir, "Results", nameOfInstanceCSV)
    archiveTTL = "rawArchive.ttl"
    instanceLevelTTL = "instanceLevel.ttl"
    rootDirectory= sys.argv[1]
    headerSetFlag = False
    cleanedList = []
    couponList = list()
    dirList = list()
    oneTimeFlag = True
    #==============================================================================
    #creating the header row
    
    headerRow = ["FullFilePath","FileTypes", "CurrentDirectoryName","SeriesName",\
                 "AllFileList", "CouponName", "Series","Panel", "Coupon"]
    
    #============================================================================== 
    
    
    #creating the CSV file=========================================================
    with open(instanceCSV_file_path, 'w',newline='') as csvFile:
        w = csv.writer(csvFile)
        w.writerow(headerRow)
        headerforDir = ['currentDirectory','currLabel', 'Depth','parentDirectory','PLabel', 'childDirectory', 'CLabel', \
                        'NumOfFilesInside', 'NumofSubDir', 'SubDirLabels', 'FilePathsInsideCurr']
        with open(archiveCSV_file_path, 'w',newline='') as csvFileD:
            ww = csv.writer(csvFileD)
            ww.writerow(headerforDir)#write the header row
            for dirName, subDirList, imFileList in os.walk(rootDirectory):
                depth = len(dirName.rstrip(os.path.sep).split(os.path.sep))#find the depth of the curr dir
                currLabel = dirName.rstrip(os.path.sep).split(os.path.sep)[-1]#current directory label 
                fullFilePath = getFullFilePath(imFileList, dirName) #get full path names for files.
                temp = (dirName+os.path.sep).count(os.path.sep)
                if(oneTimeFlag == True ):
                    dirDepth = dirName.count(os.path.sep)
                    currDepth = 'root'
                if(temp - dirDepth == 1 and oneTimeFlag == False):
                    currDepth = 'experiment'
                if(temp - dirDepth >= 2 and oneTimeFlag == False):
                    currDepth = 'result' 
                oneTimeFlag = False
                if depth >1:
                    isOfSubDir = (os.path.sep).join((dirName.rstrip(os.path.sep).split(os.path.sep)[:-1])) #the parent directory
                    Plabel = (dirName.rstrip(os.path.sep).split(os.path.sep)[-2])#parent directory label
                else:
                    isOfSubDir = ''
                    Plabel =''
                dirList = [dirName.strip().replace(' ','_'), currLabel.strip().replace(' ','_'),currDepth,\
                           isOfSubDir.strip().replace(' ','_') ,Plabel.strip().replace(' ','_'),'','',\
                            len(imFileList),len(subDirList),','.join(subDirList).strip().replace(' ','_'),\
                            ','.join(fullFilePath).strip().replace(' ','_')]
                try:
                    ww.writerow(dirList)#write the header of each level          
                except:
                    pass
                
                #for the stuff inside the subdirectories
                for bfsDir in subDirList:
                    currDepth = ''
                    if(dirName[-1] != os.path.sep):
                        temp = (dirName+os.path.sep).count(os.path.sep)
                        if(temp - dirDepth == 1):
                            currDepth = 'experiment'
                        if(temp - dirDepth >= 2):
                            currDepth = 'result' 
                    depth = len(dirName.rstrip(os.path.sep).split(os.path.sep))
                    currLabel = dirName.rstrip(os.path.sep).split(os.path.sep)[-1]#current directory label
                    filePathForSD = getFullFilePath(imFileList, dirName) #get full path names for files.
                    if depth >1:
                        isOfSubDir = (os.path.sep).join((dirName.rstrip(os.path.sep).split(os.path.sep)[:-1])) #the parent directory
                        Plabel = (dirName.rstrip(os.path.sep).split(os.path.sep)[-2])
                    else:
                        isOfSubDir = ''
                        Plabel = ''

                    Clabel = bfsDir.split(os.path.sep)[-1]
                    dirList = [dirName.strip().replace(' ','_') , currLabel.strip().replace(' ','_'),currDepth,\
                               isOfSubDir.strip().replace(' ','_'), Plabel.strip().replace(' ','_') ,\
                                 os.path.join(dirName, bfsDir).strip().replace(' ','_') ,Clabel.strip().replace(' ','_'),\
                                 len(imFileList), '','',','.join(filePathForSD).strip().replace(' ' ,'_')]
                    try:
                        ww.writerow(dirList)
                    except:
                        pass
                
                #for individual files
                for fileName in fnmatch.filter(imFileList, '*.*'):
                    filePath = os.path.join(dirName, fileName).strip().replace(' ','_')
                    currentDirName = dirName.rstrip(os.path.sep).split(os.path.sep)[-1].strip().replace(' ','_')
                    couponName = getCouponName(fileName)
                    splitcoupon = couponName.split('-') if len(couponName) != 0 else ['','','']
                    cleanedList = [filePath.strip().replace('\\','/'), getFileTypes(fileName),  dirName.strip().replace('\\','/'),\
                                   getSeries(dirName),fileName.strip().replace(' ','_'), couponName, str(splitcoupon[0]),\
                                    str(splitcoupon[1]), str(splitcoupon[2])]
                    if(len(couponName)>0):             
                        splitcoupon.insert(0,couponName)
                    if (len(cleanedList) != 0):
                        try:    
                            w.writerow(cleanedList)
                        except:
                            pass
                
    #closing the CSV file=========================================================
    csvFile.close()
    csvFileD.close()
    print("Conversion done.\nFilenames are --> ")
    print("1. For Directory Structure  - {} \n2. For FileStructure Associated with domain knowledge - {}".format(nameOfDirectoryCSV,nameOfInstanceCSV))
    print("Invoking Setlr")
    #setlr.mainFunc("setlr_params.ttl")
    archive_file_path = os.path.join(current_file_dir, "params", "setlr_params_domain.ttl")
    instance_file_path = os.path.join(current_file_dir, "params", "setlr_params_instancelevel.ttl")
    setNamesOfFilesinParamsTTl(archive_file_path, "setlr_params_domain.ttl",  nameOfDirectoryCSV, archiveTTL )
    setNamesOfFilesinParamsTTl(instance_file_path, "setlr_params_instancelevel.ttl", nameOfInstanceCSV, instanceLevelTTL )
    setlr.mainFunc(os.path.join(os.path.dirname(__file__), "Results", "setlr_params_domain.ttl"))
    setlr.mainFunc(os.path.join(os.path.dirname(__file__), "Results", "setlr_params_instancelevel.ttl"))
    sleep(5)
    fp = open(os.path.join(os.path.dirname(__file__), "Results", instanceLevelTTL), "a")
    fd = open(os.path.join(os.path.dirname(__file__), "Results", archiveTTL), "r")
    # #join the two turtle files together
    lines = fd.readlines()
    for i in range(2):
        fp.write("\n")
    for line in lines:
        if line[0]!='@':
            fp.write(line)
            fp.write("\n")
    fp.close()
    fd.close()
	#==================================
    print("Conversion done, rdf turtle file for folder structure : graphDirectory.ttl")
    print("Conversion done, rdf turtle file for domain instance level map : graphDirectoryInstance.ttl")