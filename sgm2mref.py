#!/usr/bin/env python3

import sys
from sgmllib import SGMLParser
import optparse

def normalize(reference):
    return reference.replace("#", "\\#").replace("\n", " ").strip()

class ReferenceSet:
    def __init__(self):
        self.references = []
        self.keys = {}

    def addReference(self, key, reference):
        if key in self.keys:
            self.keys[key].append(reference)
        else:
            self.references.append([reference])
            self.keys[key] = self.references[-1]

    def printReferences(self, output):
        for refSet in self.references:
            output.write(normalize(refSet[0]))
            for r in refSet[1:]:
                output.write(f" # {normalize(r)}")
            output.write("\n")

class SGMLRefParser(SGMLParser):
    def __init__(self, referenceSet, verbose):
        super.__init__(self)
        self.referenceSet = referenceSet
        self.inSegment = False
        self.verbose = verbose
        self.lastReference = None

    def start_doc(self, attributes):
        if self.verbose:
            sys.stderr.write(f"start_doc {str(attributes)}\n")
        self.basekey = ""
        for a in attributes:
            if a[0] != "sysid":
                self.basekey += ("%s#" % a[1])

    def start_seg(self, attributes):
        if self.verbose:
            sys.stderr.write(f"start_seg {str(attributes)}\n")
        for a in attributes:
            if a[0] == "id":
                self.segid = a[1]
        self.inSegment = True

    def end_seg(self):
        if self.verbose:
            sys.stderr.write("end_seg\n")
        if self.inSegment:
            self.referenceSet.addReference(f"{self.basekey}#{self.segid}", self.lastReference)
            self.inSegment = False
            self.lastReference = None

    def handle_data(self, data):
        if self.verbose:
            sys.stderr.write(f"data: {data}\n")
        if self.inSegment:
            if self.lastReference:
                self.lastReference += f" {data.strip()}"
            else:
                self.lastReference = data.strip()
            

def main():
    usage = "usage: %prog [options] sgmfile"
    optionParser = optparse.OptionParser(usage=usage)
    optionParser.add_option("-o", "--out", metavar="file", dest="outFilename", help="output file")
    optionParser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                            help="write every step to stderr, useful for finding errors in sgml files")
    (options, args) = optionParser.parse_args()

    if len(args) == 0:
        fpIn = sys.stdin
    else:
        try:
            fpIn = open(args[0])
        except IOError as ioError:
            optionParser.error(f"couldn't open {args[0]}, {ioError}")

    if not options.outFilename:
        fpOut = sys.stdout
    else:
        try:
            fpOut = open(options.outFilename, "w")
        except IOError as ioError:
            optionParser.error(f"couldn't open {options.outFilename} for writing, {ioError}")
            
    referenceSet = ReferenceSet()
    parser = SGMLRefParser(referenceSet, options.verbose)
    parser.feed(fpIn.read())
    referenceSet.printReferences(fpOut)
    
if __name__ == "__main__":
    main()
