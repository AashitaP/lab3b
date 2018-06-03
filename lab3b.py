import argparse
import csv
import sys
import os
from __future__ import print_function

csvfile = ""
superblock = None
group = None
freeBlocks = []
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
            x += 1
        
class Indirect:
    def __init__(self, arg):
        self.inodeNumber = int(arg[1])
        self.levelIndirection = int(arg[2])
        self.offset = int(arg[3])
        self.blockNumberIndirect = int(arg[4])
        self.blockNumberReferenced = int(arg[5])




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
                    freeBlocks.append(Bfree(row))
                elif row[0] == "IFREE":
                    global freeInodes
                    freeInodes.append(Ifree(row))
                elif row[0] == "INODE":
                    global inodes
                    inodes.append(Inode(row))
                elif row[0] == "DIRENT":
                    global dirEntries
                    dirEntries.append(Directory(row))
                elif row[0] == "INDIRECT":
                    global indirects
                    indirects.append(Indirect(row))
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

    

