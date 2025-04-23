import os
import re
from typing import Any

python_compile = compile


def process_includes(filename: str, include_folder: str) -> tuple[str, set[str]]:
    """Process template includes, replacing include directives with file contents.

    Args:
        filename: Path to the template file
        include_folder: Directory containing included files

    Returns:
        Tuple of processed template text and set of dependency file paths
    """
    data = open(filename).read()
    dependencies: set[str] = set()

    while True:
        match = re.search(r'\[%-\s+include\s+"([^"]*)"\s*-%\]', data)
        if not match:
            break
        name = match.group(1)
        path = os.path.join(include_folder, name)
        dependencies.add(path)
        included_file = open(path).read()
        data = data[: match.start()] + included_file + data[match.end() :]
    return data, dependencies


def compile(filename: str, include_folder: str) -> tuple[Any, set[str]]:
    """Compile template file into Python code.

    Args:
        filename: Path to the template file
        include_folder: Directory containing included files

    Returns:
        Tuple of compiled code object and set of dependency file paths
    """
    data, dependencies = process_includes(filename, include_folder)

    output = """
global output
output = ""
"""
    last_free = 0
    indent = ""

    for match in re.finditer(r"\[%(-|=)\s+([a-zA-Z][a-zA-Z0-9_.]*)\s+(.*?)\s*-?%\]", data):
        if match.start() > last_free:
            output += f"{indent}output += '''{data[last_free : match.start()]}'''\n"
            last_free = match.end()
        if match.group(1) == "=":
            output += f"{indent}output += {match.group(2)}\n"
        elif match.group(2) == "if":
            output += f"{indent}if {match.group(3)}:\n"
            indent += "    "
        elif match.group(2) == "for":
            output += f"{indent}for {match.group(3)}:\n"
            indent += "    "
        elif match.group(2) == "else":
            output += f"{indent[: len(indent) - 4]}else:\n"
        elif match.group(2) == "end":
            indent = indent[: len(indent) - 4]
        else:
            raise Exception(f"Unknown thing {match.group(2)}")
    output += f'{indent}output += """{data[last_free:]}"""\n'
    f = open(r"/tmp/test.txt", "w")
    f.write(output)
    f.close()
    return python_compile(output, filename, "exec"), dependencies


def process(filename: str, includePath: str, dictionary: dict[str, Any]) -> tuple[str, set[str]]:
    """Process a template with provided data dictionary.

    Args:
        filename: Path to the template file
        includePath: Directory containing included files
        dictionary: Data to use when rendering the template

    Returns:
        Tuple of rendered output text and set of dependency file paths
    """
    dict_copy = dict(dictionary)
    compiled_code, deps = compile(filename, includePath)
    exec(compiled_code, dict_copy)
    return dict_copy["output"], deps


if __name__ == "__main__":

    class Article:
        def __init__(self, name: str):
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

    code, deps = compile(r"../conf/frontpage-template.html", r"../conf")
    globalDict = {
        "label": {"name": "bob", "filename": "denzel"},
        "latestUpdateISO": "hello",
        "year": "2007",
        "articles": [Article("one"), Article("two")],
    }
    exec(code, globalDict)
    print(globalDict["output"])
    print(deps)
