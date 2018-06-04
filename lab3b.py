from __future__ import print_function
import csv
import sys
import os

csvfile = ""
superblock = None
group = None
freeBlocks = set()
allocatedBlocks = set()
duplicateBlocks = dict()
freeInodes = []
inodes = []
dirEntries = []
indirects = []

class Superblock:
    def __init__(self, arg):
        self.blockCount = int(arg[1])
        self.inodeCount = int(arg[2])
        self.blockSize = int(arg[3])
        self.inodeSize = int(arg[4])
        self.blocksPG = int(arg[5])
        self.inodesPG = int(arg[6])
        self.firstNonReserved = int(arg[7])

class Group:
    def __init__(self, arg):
        self.numberBlocks = int(arg[2])
        self.numberInodes = int(arg[3])
        self.freeBlocks = int(arg[4])
        self.freeInodes = int(arg[5])
        self.bitmap = int(arg[6])
        self.inodemap = int(arg[7])
        self.firstInode = int(arg[8])

class Inode:
    def __init__(self, arg):
        self.inodeNumber = int(arg[1])
        self.fileType = arg[2]
        self.owner = int(arg[4])
        self.group = int(arg[5])
        self.linkCount = int(arg[6])
        self.fileSize = int(arg[10])
        self.numberBlocks = int(arg[11])
        x = 12
        for i in range(0, 15):
            self.blockAddresses[i] = int(arg[x])
            allocatedBlocks.add(int(arg[x]))
            x += 1
        
class Indirect:
    def __init__(self, arg):
        self.inodeNumber = int(arg[1])
        self.levelIndirection = int(arg[2])
        self.offset = int(arg[3])
        self.blockNumberIndirect = int(arg[4])
        blockNumber = int(arg[5])
        self.blockNumberReferenced = blockNumber
        global allocatedBlocks
        global duplicateBlocks
        allocatedBlocks.add(blockNumber)
        if blockNumber not in duplicateBlocks:
            duplicateBlocks[blockNumber] = list()
        duplicateBlocks[blockNumber].append((self.inodeNumber, self.offset)) #not sure what offset to use

def checkBlockConsistency():
    global superblock
    global duplicateBlocks
    global allocatedBlocks
    global freeBlocks
    #examine every block pointer in every single inode, directory block, indirect block, double indirect block, triple indirect block
    for inode in inodes: #first check invalid and reserved blocks by examining block pointers in inode
        i = 1
        for pointer in inode.blockAddresses:
            if(pointer < 0 or pointer > superblock.blockCount): #check invalid
                if i <= 12:
                    print ("INVALID BLOCK %d IN INODE %d AT OFFSET 0" %(pointer,inode.inodeNumber))
                elif i == 13:
                    print ("INVALID INDIRECT BLOCK %d IN INODE %d AT OFFSET 12" %(pointer,inode.inodeNumber))
                elif i == 14:
                    print ("INVALID DOUBLE INDIRECT BLOCK %d IN INODE %d AT OFFSET 268" %(pointer,inode.inodeNumber))
                elif i == 15:
                    print ("INVALID TRIPLE INDIRECT BLOCK %d IN INODE %d AT OFFSET 65804" %(pointer,inode.inodeNumber))
            elif(pointer < 8 and pointer != 0): #check reserved #why???
                if i <= 12:
                    print ("RESERVED BLOCK %d IN INODE %d AT OFFSET 0" %(pointer,inode.inodeNumber))
                elif i == 13:
                    print ("RESERVED INDIRECT BLOCK %d IN INODE %d AT OFFSET 12" %(pointer,inode.inodeNumber))
                elif i == 14:
                    print ("RESERVED DOUBLE INDIRECT BLOCK %d IN INODE %d AT OFFSET 268" %(pointer,inode.inodeNumber))
                elif i == 15:
                    print ("RESERVED TRIPLE INDIRECT BLOCK %d IN INODE %d AT OFFSET 65804" %(pointer,inode.inodeNumber))
            if pointer not in duplicateBlocks:
                duplicateBlocks[pointer] = list()
            if i <= 12:
                duplicateBlocks[pointer].append((inode.inodeNumber, 0))
            elif i == 13:
                duplicateBlocks[pointer].append((inode.inodeNumber, 12))
            elif i == 14:
                duplicateBlocks[pointer].append((inode.inodeNumber, 268))
            elif i == 15:
                duplicateBlocks[pointer].append((inode.inodeNumber, 65804))
            i += 1        
    for i in range(8, superblock.blockCount):
        if i not in freeBlocks and allocatedBlocks:
            print ("UNREFERENCED BLOCK %d" %(i))
    for block in allocatedBlocks:
        if block in freeBlocks:
            print("ALLOCATED BLOCK %d ON FREELIST")
    for key, value in duplicateBlocks.items():
        if len(value) > 1:
            for duplicate in value:
                if (int(duplicate[1])) >= 65804:
                    print("DUPLICATE TRIPLE INDIRECT BLOCK %d IN INODE %d AT OFFSET %d" %(key, duplicate[0], duplicate[1]))
                elif (int(duplicate[1])) >= 268:
                    print("DUPLICATE DOUBLE INDIRECT BLOCK %d IN INODE %d AT OFFSET %d" %(key, duplicate[0], duplicate[1]))
                elif (int(duplicate[1])) >= 12:
                    print("DUPLICATE INDIRECT BLOCK %d IN INODE %d AT OFFSET %d" %(key, duplicate[0], duplicate[1]))
                else:
                    print("DUPLICATE BLOCK %d IN INODE %d AT OFFSET %d" %(key, duplicate[0], duplicate[1]))







def main():
    if (len(sys.argv) != 2):
        sys.stderr.write("Usage: Require one argument - a csv file")
        exit(1)
    global csvfile
    csvfile = sys.argv[1]
    with open(csvfile, 'rb') as opencsvfile:
        reader = csv.reader(opencsvfile)
        try:
            for row in reader: #basically storing all the information from the csv file
                if row[0] == "SUPERBLOCK":
                    global superblock 
                    superblock = Superblock(row)
                elif row[0] == "GROUP":
                    global group
                    group = Group(row)
                elif row[0] == "BFREE":
                    global freeBlocks
                    freeBlocks.add(int(row[1]))
               # elif row[0] == "IFREE":
                #    global freeInodes
                 #   freeInodes.append(Ifree(row))
                elif row[0] == "INODE":
                    global inodes
                    inodes.append(Inode(row))
               # elif row[0] == "DIRENT":
                  #  global dirEntries
                   # dirEntries.append(Directory(row))
                elif row[0] == "INDIRECT":
                    global indirects
                    indirects.append(Indirect(row))
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (csvfile, reader.line_num, e))

    

