import os, re

python_compile = compile


def process_includes(filename, include_folder):
    data = open(filename, 'r').read()
    dependencies = set()

    while True:
        match = re.search(r'\[%-\s+include\s+"([^"]*)"\s*-%\]', data)
        if not match:
            break
        name = match.group(1)
        path = os.path.join(include_folder, name)
        dependencies.add(path)
        included_file = open(path, 'r').read()
        data = data[:match.start()] + included_file + data[match.end():]
    return data, dependencies


def compile(filename, include_folder):
    data, dependencies = process_includes(filename, include_folder)

    output = """
global output
output = ""
"""
    last_free = 0
    indent = ""

    for match in re.finditer(r'\[%(-|=)\s+([a-zA-Z][a-zA-Z0-9_.]*)\s+(.*?)\s*-?%\]', data):
        if match.start() > last_free:
            output += indent + "output += '''%s'''\n" % data[last_free:match.start()]
            last_free = match.end()
        if match.group(1) == '=':
            output += indent + "output += %s\n" % match.group(2)
        elif match.group(2) == "if":
            output += indent + "if %s:\n" % match.group(3)
            indent += "    "
        elif match.group(2) == "for":
            output += indent + "for %s:\n" % match.group(3)
            indent += "    "
        elif match.group(2) == "else":
            output += indent[:len(indent) - 4] + "else:\n"
        elif match.group(2) == "end":
            indent = indent[:len(indent) - 4]
        else:
            raise Exception("Unknown thing " + match.group(2))
    output += indent + 'output += """%s"""\n' % data[last_free:]
    f = open(r'/tmp/test.txt', 'w')
    f.write(output)
    f.close()
    return python_compile(output, filename, "exec"), dependencies


def process(filename, includePath, dictionary):
    dict_copy = dict(dictionary)
    compiled_code, deps = compile(filename, includePath)
    exec(compiled_code, dict_copy)
    return dict_copy['output'], deps


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
            self.permalink = "https://xania.org"


    code, deps = compile(r'../conf/frontpage-template.html', r'../conf')
    globalDict = dict()
    globalDict['label'] = {"name": "bob", "filename": "denzel"}
    globalDict['latestUpdateISO'] = "hello"
    globalDict['year'] = "2007"
    globalDict['articles'] = [article("one"), article("two")]
    exec(code, globalDict)
    print(globalDict['output'])
    print(deps)
