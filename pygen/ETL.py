import os, re

def ProcessIncludes(filename, includeFolder):
    data = open(filename, 'r').read()
    dependencies = set()

    while True:
        match = re.search(r'\[%-\s+include\s+"([^"]*)"\s*-%\]', data)
        if not match:
            break
        name = match.group(1)
        path = os.path.join(includeFolder, name)
        dependencies.add(path)
        includedFile = open(path, 'r').read()
        data = data[:match.start()] + includedFile + data[match.end():]
    return data, dependencies

def Compile(filename, includeFolder):
    data, dependencies = ProcessIncludes(filename, includeFolder)
    
    output = """
global output
output = ""
"""
    lastFree = 0
    indent = ""
        
    for match in re.finditer(r'\[%(-|=)\s+([a-zA-Z][a-zA-Z0-9_.]*)\s+(.*?)\s*-?%\]', data):
        if match.start() > lastFree:
            output += indent + "output += '''%s'''\n" % data[lastFree:match.start()]
            lastFree = match.end()
        if match.group(1) == '=':
            output += indent + "output += %s\n" % match.group(2)
        elif match.group(2) == "if":
            output += indent + "if %s:\n" % match.group(3)
            indent += "    "
        elif match.group(2) == "for":
            output += indent + "for %s:\n" % match.group(3)
            indent += "    "
        elif match.group(2) == "else":
            output += indent[:len(indent)-4] + "else:\n"
        elif match.group(2) == "end":
            indent = indent[:len(indent)-4]
        else:
            raise Exception, "Unknown thing " + match.group(2)
    output += indent + 'output += """%s"""\n' % data[lastFree:]
    #f = open(r'c:\temp\test.txt', 'w')
    #f.write(output)
    #f.close()
    return compile(output, filename, "exec"), dependencies

def Process(filename, includePath, dictionary):
    dictCopy = dict(dictionary)
    compiledCode, deps = Compile(filename, includePath)
    exec compiledCode in dictCopy
    return dictCopy['output'], deps

if __name__ == "__main__":
    class article:
        def __init__(self, name):
            self.title = name
            self.basename = "baysname"
            self.basenameNAME = "baysnameNAME"
            self.summary = "a summary"
            self.contentHTML = "<moo></moo>"
            self.contentXHTML = "<moo></moo>"
            self.via = ""
            self.datesAtom = "date"
            self.dateHTML = "<date>"
            self.dateISO = "<date>"
            self.permalink = "http://xania.org"

    code, deps = Compile(r'C:\Codebase\mbs\conf\frontpage-template.html', r'C:\Codebase\mbs\conf')
    globalDict = dict()
    globalDict['label'] = "hello"
    globalDict['latestUpdateISO'] = "hello"
    globalDict['year'] = "2007"
    globalDict['articles'] = [article("one"), article("two")]
    exec code in globalDict
    print globalDict['output']
    print deps
    
