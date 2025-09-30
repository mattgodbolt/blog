#!/usr/bin/env python
import codecs
import datetime
import os
import re
from collections.abc import Callable
from datetime import timedelta
from datetime import timezone as dt_timezone
from typing import Any, Optional
from warnings import warn
from xml.etree import ElementTree

import pygments
import pygments.lexers
from markdown import markdown
from pytz import timezone, utc

from pygen import ETL
from pygen.precis import PrecisExtension

pygments.lexers.LEXERS["AsmLexer"] = ("pygen.asm_lexer", "AsmLexer", ("asm",), ("*.asm",), ("text/asm"))
pygments.lexers.LEXERS["BasicLexer"] = ("pygen.basic_lexer", "BasicLexer", ("basic",), ("*.basic",), ("text/basic"))
pygments.lexers.LEXERS["HexasmLexer"] = (
    "pygen.hexasm_lexer",
    "HexasmLexer",
    ("hexasm",),
    ("*.hexasm",),
    ("text/hexasm"),
)

# Default timezone for articles that don't specify one
defaultTimeZone = timezone("Europe/London")


class GlobalData:
    """A holding structure for global data.  Nicer than global variables."""

    def __init__(self):
        # The config dictionary stores both strings and other values like booleans
        self.config: dict[str, Any] = {}
        self.articles: dict[str, "Article"] = {}
        self.labels: set["Label"] = set()

    def GetValue(self, value: str, label: Optional["Label"]) -> str:
        """Get a configuration value, optionally with label-specific overrides.

        Args:
            value: Configuration key to look up
            label: Optional label to use for label-specific overrides

        Returns:
            Configuration value or empty string if not found
        """
        if label:
            labelName = f"{value}.{label.name}"
            if labelName in self.config:
                result = self.config[labelName]
                return str(result) if result is not None else ""
            wildcardName = f"{value}.*"
            if wildcardName in self.config:
                result = self.config[wildcardName]
                return str(result).replace("*", label.filename) if result is not None else ""
            return ""
        else:
            result = self.config.get(value, "")
            return str(result) if result is not None else ""

    def GetInheritedValue(self, value: str, label: Optional["Label"]) -> str:
        """Get a required configuration value, optionally with label-specific overrides.

        Args:
            value: Configuration key to look up
            label: Optional label to use for label-specific overrides

        Returns:
            Configuration value (throws exception if not found)
        """
        if label:
            labelName = f"{value}.{label.name}"
            if labelName in self.config:
                result = self.config[labelName]
                return str(result) if result is not None else ""
            wildcardName = f"{value}.*"
            if wildcardName in self.config:
                result = self.config[wildcardName]
                return str(result).replace("*", label.filename) if result is not None else ""

        result = self.config[value]
        return str(result) if result is not None else ""

    def GetInheritedInt(self, value: str, label: Optional["Label"]) -> int:
        """Get a required configuration value as integer, with optional label-specific overrides.

        Args:
            value: Configuration key to look up
            label: Optional label to use for label-specific overrides

        Returns:
            Configuration value as integer
        """
        return int(self.GetInheritedValue(value, label))

    def GetPublicArticles(self, label: Optional["Label"]) -> list["Article"]:
        """Get public articles, optionally filtered by label.

        Args:
            label: Optional label to filter articles by

        Returns:
            List of public articles
        """

        def is_public_with_label(article: "Article") -> bool:
            return article.Status == "public" and label in article.Labels

        def is_public(article: "Article") -> bool:
            return article.Status == "public"

        if label:
            filter_func: Callable[["Article"], bool] = is_public_with_label
        else:
            filter_func = is_public
        return list(filter(filter_func, list(self.articles.values())))


class Article:
    """An article with metadata and content."""

    def __init__(self, globalData: GlobalData, name: str):
        self.BaseName = name.replace("\\", "/")
        self.ArticleModified = 0
        self.HtmlModified = 0
        self.Status = "public"
        self.Author = globalData.config["DefaultArticleAuthor"]
        self.LicenseURL = globalData.config["DefaultArticleLicenseURL"]
        self.Dates: list[datetime.datetime] = []
        self.Labels: list["Label"] = []
        self.Summary = ""
        self.Via = ""
        self.ArticleText = ""
        self.HtmlText = ""
        self.HtmlIntro = ""
        self.XHtmlText = ""
        self.RawTitle = ""
        self.Title = ""
        self.URLPrefix = globalData.config["ArticleURLPrefix"]
        self.PrevArticle: "Article" | None = None
        self.NextArticle: "Article" | None = None

    def __getattr__(self, name: str) -> Any:
        """Get attributes using case-insensitive names and computed properties.

        Args:
            name: Attribute name to retrieve

        Returns:
            Attribute value

        Raises:
            AttributeError: If attribute not found
        """
        name = name.lower()
        if name == "title":
            return self.Title
        elif name == "contenthtml":
            return self.HtmlText
        elif name == "introhtml":
            return self.HtmlIntro
        elif name == "contentxhtml":
            return self.XHtmlText
        elif name == "basename":
            return self.BaseName
        elif name == "summary":
            return self.Summary
        elif name == "via":
            return self.Via
        elif name == "basenamename":
            return "a" + re.sub("[^a-zA-Z0-9.-]", "_", self.BaseName)
        elif name == "datehtml":
            return FormatHtmlDate(self.Dates[0])
        elif name == "dateiso":
            return FormatISODate(self.Dates[0])
        elif name == "datesatom":
            return FormatAtomDates(self.Dates)
        elif name == "datemonth":
            return self.Dates[0].strftime("%B %Y")
        elif name == "permalink":
            return self.URLPrefix + self.BaseName
        elif name == "datemonthprev":
            return self.PrevArticle and self.PrevArticle.DateMonth or ""
        elif name == "labels":
            return self.Labels

        raise AttributeError(f"Unknown attribute {name}")


class Label:
    """Holds information about a label (category)."""

    def __init__(self, name: str):
        self.name = name
        self.filename = name.replace(" ", "-")

    def __lt__(self, other: "Label") -> bool:
        return self.name < other.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Label):
            return NotImplemented
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return f"Label({self.name})"


def ReadGeneratorConfig(filename: str, globalData: GlobalData) -> None:
    """Read configuration from a file into the GlobalData object.

    Args:
        filename: Path to configuration file
        globalData: Global data object to store configuration in
    """
    lineNumber = 0

    for line in open(filename):
        lineNumber += 1
        line = line.strip()
        # Skip empty lines and comment lines
        if not line or line[0] == "#":
            continue
        try:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key in globalData.config:
                warn(f"{filename}:{lineNumber} : Duplicate key '{key}'", stacklevel=2)
            globalData.config[key] = value
        except ValueError:
            warn(f"{filename}:{lineNumber} : Missing ':'", stacklevel=2)


def CheckConfig(globalData: GlobalData) -> None:
    """Validate configuration settings.

    Args:
        globalData: Global data object with configuration to validate

    Raises:
        Exception: If configuration is invalid
    """

    def IsPresent(key: str) -> None:
        if key not in globalData.config:
            raise Exception(f"Missing required configuration option '{key}'")

    def IsDir(key: str) -> None:
        IsPresent(key)
        if not os.path.isdir(globalData.config[key]):
            raise Exception(f"Missing directory '{globalData.config[key]}' for configuration option '{key}'")

    def IsFile(key: str) -> None:
        IsPresent(key)
        if not os.path.isfile(globalData.config[key]):
            raise Exception(f"Missing file '{globalData.config[key]}' for configuration option '{key}'")

    def CreateDummy(key: str, value: str = "") -> None:
        """Create a config entry if it doesn't exist.

        Args:
            key: Configuration key to check/create
            value: Default value to set if key doesn't exist
        """
        if key not in globalData.config:
            globalData.config[key] = value

    def IsNumber(key: str) -> None:
        IsPresent(key)
        try:
            value = int(globalData.config[key])
            if value <= 1:
                raise Exception(f"Invalid numeric value {value} (< 1) for configuration option '{key}'")
        except ValueError as err:
            val = globalData.config[key]
            raise Exception(f"Invalid numeric value '{val}' for configuration option '{key}'") from err

    IsDir("ArticleDirectory")
    IsPresent("ArticleURLPrefix")
    IsFile("ArticleTemplate")

    # Check if FrontPageTemplate is already defined
    has_frontpage = "FrontPageTemplate" in globalData.config
    if not has_frontpage:
        CreateDummy("FrontPageTemplate")
    if has_frontpage:
        IsFile("FrontPageTemplate")
        IsPresent("FrontPageArticleCount")
        IsPresent("FrontPageOutput")

    # Check if AtomFeedTemplate is already defined
    has_atomfeed = "AtomFeedTemplate" in globalData.config
    if not has_atomfeed:
        CreateDummy("AtomFeedTemplate")
    if has_atomfeed:
        IsFile("AtomFeedTemplate")
        IsPresent("AtomFeedArticleCount")
        IsPresent("AtomFeedOutput")

    # Check if ArchiveTemplate is already defined
    has_archive = "ArchiveTemplate" in globalData.config
    if not has_archive:
        CreateDummy("ArchiveTemplate")
    if has_archive:
        IsFile("ArchiveTemplate")
        IsPresent("ArchiveOutput")

    CreateDummy("DefaultArticleAuthor")
    CreateDummy("DefaultArticleLicenseURL")

    IsNumber("FrontPageArticleCount")
    IsNumber("AtomFeedArticleCount")


def GetArticle(globalData, name):
    if name not in globalData.articles:
        globalData.articles[name] = Article(globalData, name)
    return globalData.articles[name]


def ScanArticleDirectory(globalData):
    articleDir = os.path.abspath(globalData.config["ArticleDirectory"])
    for root, dirs, files in os.walk(articleDir):
        for filename in files:
            fullPath = os.path.join(root, filename)
            basename, extension = os.path.splitext(filename)
            basename = os.path.join(root, basename)[len(articleDir) + 1 :]
            if extension == ".html":
                article = GetArticle(globalData, basename)
                article.HtmlModified = os.path.getmtime(fullPath)
            elif extension == ".text":
                article = GetArticle(globalData, basename)
                article.TextModified = os.path.getmtime(fullPath)
        if ".svn" in dirs:
            dirs.remove(".svn")


def ParseDate(date):
    """Parse date with optional timezone information.

    Formats supported:
    - YYYY-MM-DD
    - YYYY-MM-DD HH
    - YYYY-MM-DD HH:MM
    - YYYY-MM-DD HH:MM:SS
    - YYYY-MM-DD HH:MM:SS TZNAME (e.g., America/Chicago)
    - YYYY-MM-DD HH:MM:SS ±HHMM (e.g., -0500, +0100)
    - YYYY-MM-DD HH:MM:SS ±HH:MM (e.g., -05:00, +01:00)

    If no timezone is specified, the default timezone (Europe/London) is used.
    """
    # First, try to match the date and time part
    match = re.match(r"\s*(\d\d\d\d)-(\d\d)-(\d\d)(?:\s+(\d\d)(?::(\d\d)(?::(\d\d))?)?)?(.*)", date)

    if not match:
        raise ValueError(f'Invalid date string "{date}"')

    year, month, day, hour, minute, second, tz_part = match.groups()
    year, month, day = int(year), int(month), int(day)
    hour = int(hour or 0)
    minute = int(minute or 0)
    second = int(second or 0)
    tz_part = tz_part.strip() if tz_part else ""

    # Create a naive datetime
    local_dt = datetime.datetime(year, month, day, hour, minute, second, 0)

    # Process timezone if provided
    if tz_part:
        # Try to match offset timezone format with or without colon (e.g., -0500, +0100, -05:00, +01:00)
        # Format: +/-HH:MM or +/-HHMM
        tz_offset_match = re.match(r"([+-])(\d\d)(?::)?(\d\d)", tz_part)
        if tz_offset_match:
            sign, offset_hours, offset_minutes = tz_offset_match.groups()
            offset_hours, offset_minutes = int(offset_hours), int(offset_minutes)
            total_offset = offset_hours * 60 + offset_minutes
            if sign == "-":
                total_offset = -total_offset

            # Convert offset to seconds
            offset_seconds = total_offset * 60
            custom_tz = dt_timezone(timedelta(seconds=offset_seconds))
            return local_dt.replace(tzinfo=custom_tz)

        # Try to use it as a named timezone
        try:
            named_tz = timezone(tz_part)
            try:
                return named_tz.localize(local_dt, is_dst=None)
            except Exception as e:
                raise ValueError(f'Error localizing date with timezone "{tz_part}": {e!s}') from e
        except Exception as e:
            raise ValueError(f'Invalid timezone name "{tz_part}": {e!s}') from e

    # If no timezone was specified, use default
    return defaultTimeZone.localize(local_dt, is_dst=None)


def ReadArticle(globalData, article):
    processingHeader = True
    filename = os.path.join(globalData.config["ArticleDirectory"], article.BaseName + ".text")
    try:
        fileHandle = codecs.open(filename, "r", "utf8")
    except OSError as err:
        print(f"Ignoring article '{filename}' as cannot open: {err}")
        return
    article.RawTitle = fileHandle.readline().strip()
    # Strip the BOM, if needed.
    article.RawTitle = article.RawTitle.lstrip(str(codecs.BOM_UTF8, "utf8"))
    print("Read article", article.RawTitle)
    article.ArticleText = ""
    headers = {}
    lineNumber = 1
    for line in fileHandle:
        lineNumber += 1
        if processingHeader:
            line = line.strip()
            if not line:
                processingHeader = False
                continue
            try:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                if key in headers:
                    warn(f"{filename}:{lineNumber} : Duplicate key '{key}'", stacklevel=2)
                headers[key] = value
            except ValueError as value_err:
                raise Exception(f"{filename}:{lineNumber} : Missing ':''") from value_err
        else:
            article.ArticleText += line
    for key, value in list(headers.items()):
        if key == "status":
            value = value.lower()
            if value not in ["public", "private", "draft"]:
                raise Exception("Invalid status: '" + value + "'")
            article.Status = value
        elif key == "date":
            article.Dates = [ParseDate(val) for val in value.split(",")]
        elif key == "author":
            article.Author = value
        elif key == "licenseurl":
            article.LicenseURL = value
        elif key == "summary":
            article.Summary = value
        elif key == "via":
            article.Via = value
        elif key == "label":
            article.Labels = [Label(label.strip()) for label in value.split(",")]
        else:
            raise Exception("Invalid header: '" + key + "'")
    # Only count labels with public articles.
    if article.Status == "public":
        for label in article.Labels:
            globalData.labels.add(label)
    if not article.Dates:
        raise Exception("Missing article date(s)")


def ProcessTitle(title):
    title = re.sub("&(?!#)", "&amp;", title)
    title = title.replace("<", "&lt;")
    title = title.replace(">", "&gt;")
    return title


xhtmlToHtmlRe = re.compile(r"(<(hr|br|img|param)[^<>]*)/>")


def XHtmlToHtml(xhtml):
    """As Markdown.py doesn't have the --html4tags option, this is my quick and dirty
    xhtml to html converter."""
    return xhtmlToHtmlRe.sub(r"\1>", xhtml).replace("&nbsp;", "&#160;")


def remove_empty_spans(html):
    """Remove empty <span></span> tags inserted by Pygments.

    Pygments intentionally adds empty spans at the start of code blocks to work around
    an HTML parsing rule where browsers strip the first newline after <pre> tags.
    Since we don't need this workaround, we remove them in post-processing.
    """
    return html.replace("<span></span>", "")


def CleanUpXHtml(title, xhtml):
    full = f"<fakeroot>\n{xhtml}\n</fakeroot>"
    try:
        tree = ElementTree.fromstring(full)
        parent_map = {c: p for p in tree.iter() for c in p}
        for banned_elem_type in ("script", "iframe"):
            for elem in tree.findall(f".//{banned_elem_type}"):
                parent_map[elem].remove(elem)
        xhtml = ElementTree.tostring(next(iter(tree)), "utf-8").decode("utf-8")
    except Exception as e:
        for line, s in enumerate(full.splitlines(keepends=False)):
            print(f"{line + 1: 10}: {s}")
        raise RuntimeError(f"Bad XHTML in {title}") from e
    xhtml = xhtml.replace("&nbsp;", "&#160;")
    xhtml = re.sub("&(?!(#|amp|gt|lt|quot))", "&amp;", xhtml)
    return xhtml


def ProcessArticle(globalData, article):
    article.Title = ProcessTitle(article.RawTitle)
    print("Processing article", article.RawTitle)
    extensions = ["markdown.extensions.extra", "markdown.extensions.codehilite"]
    ex_conf = {"markdown.extensions.codehilite": {"guess_lang": False}}
    article.XHtmlText = CleanUpXHtml(
        article.RawTitle,
        markdown(article.ArticleText, extensions=extensions, extension_configs=ex_conf, output_format="xhtml"),
    )
    article.HtmlText = remove_empty_spans(
        markdown(
            article.ArticleText,
            extensions=[*extensions, "markdown.extensions.smarty"],
            extension_configs=ex_conf,
            output_format="html",
        )
    )
    article.HtmlIntro = remove_empty_spans(
        markdown(
            article.ArticleText,
            extensions=[*extensions, "markdown.extensions.smarty", PrecisExtension()],
            extension_configs=ex_conf,
            output_format="html",
        )
    )


def FormatHtmlDate(date):
    suffix = "th"
    if date.day in [1, 21, 31]:
        suffix = "st"
    if date.day in [2, 22]:
        suffix = "nd"
    if date.day in [3, 23]:
        suffix = "rd"
    return date.strftime("%X %Z on " + str(date.day) + "<sup>" + suffix + "</sup> %B %Y")


def FormatISODate(date):
    localDate = date.astimezone(utc)
    return localDate.strftime("%Y-%m-%dT%XZ")


def FormatAtomDates(dates):
    if len(dates) == 1:
        return "<updated>" + FormatISODate(dates[0]) + "</updated>"
    return (
        "<published>"
        + FormatISODate(dates[0])
        + "</published>"
        + "\n".join(["<updated>" + FormatISODate(date) + "</updated>" for date in dates[1:]])
    )


def GetArticleDict(globalData, article):
    return {
        "basename": article.BaseName,
        "basenameNAME": article.BaseNameNAME,
        "title": article.Title,
        "status": article.Status,
        "summary": article.Summary,
        "via": article.Via,
        "author": article.Author,
        "permalink": article.Permalink,
        "contentHTML": article.HtmlText,
        "contentXHTML": article.XHtmlText,
        "licenseURL": article.LicenseURL,
        "dateHTML": article.DateHTML,
        "dateISO": article.DateISO,
        "dateMonth": article.DateMonth,
        # TODO: dateMonthPrev
        "datesAtom": article.DatesAtom,
        "year": str(datetime.datetime.now().year),
        "labels": article.Labels,
        "allLabels": globalData.labels,
    }


def OutputArticleHtml(globalData, article):
    template = globalData.config["ArticleTemplate"]
    articleDirectory = globalData.config["ArticleDirectory"]
    articleHtml = os.path.join(articleDirectory, article.BaseName + ".html")
    dictionary = GetArticleDict(globalData, article)

    print("Processing article", article.RawTitle)
    html, deps = ETL.process(template, ".", dictionary)

    output = codecs.open(articleHtml, "w", "utf-8")
    output.write(html)
    output.close()


def OutputArticles(globalData, articles, template, label, outputName):
    # Find the article with the most recent update date
    latestUpdate = max(articles, key=lambda a: a.Dates[-1]).Dates[-1]
    d = {
        "year": str(datetime.datetime.now().year),
        "label": label,
        "articles": articles,
        "latestUpdateISO": FormatISODate(latestUpdate),
        "allLabels": globalData.labels,
    }
    html, deps = ETL.process(template, ".", d)
    output = codecs.open(outputName, "w", "utf-8")
    output.write(html)
    output.close()


def GenerateArticleIndices(globalData, label):
    htmlTemplate = globalData.GetInheritedValue("FrontPageTemplate", label)
    atomTemplate = globalData.GetInheritedValue("AtomFeedTemplate", label)
    archiveTemplate = globalData.GetInheritedValue("ArchiveTemplate", label)

    if not htmlTemplate and not atomTemplate and not archiveTemplate:
        return

    articleCount = globalData.GetInheritedInt("FrontPageArticleCount", label)
    feedCount = globalData.GetInheritedInt("AtomFeedArticleCount", label)

    articles = globalData.GetPublicArticles(label)

    articles.sort(key=lambda x: x.Dates[0], reverse=True)
    for i in range(len(articles)):
        if i == 0:
            articles[i].PrevArticle = None
        else:
            articles[i].PrevArticle = articles[i - 1]
        if i == len(articles) - 1:
            articles[i].NextArticle = None
        else:
            articles[i].NextArticle = articles[i + 1]

    htmlOutput = globalData.GetValue("FrontPageOutput", label)
    if htmlOutput and htmlTemplate:
        OutputArticles(globalData, articles[:articleCount], htmlTemplate, label, htmlOutput)

    atomOutput = globalData.GetValue("AtomFeedOutput", label)
    if atomOutput and atomTemplate:
        OutputArticles(globalData, articles[:feedCount], atomTemplate, label, atomOutput)

    archiveOutput = globalData.GetValue("ArchiveOutput", label)
    if archiveOutput and archiveTemplate:
        OutputArticles(globalData, articles, archiveTemplate, label, archiveOutput)


def Generate(forceGenerate: bool) -> None:
    """Generate the entire blog.

    Args:
        forceGenerate: Force regeneration of all files

    Note:
        The forceGenerate parameter is currently not used.
    """
    globalData = GlobalData()
    ReadGeneratorConfig("generator.conf", globalData)

    CheckConfig(globalData)

    ScanArticleDirectory(globalData)

    for article in globalData.articles.values():
        try:
            ReadArticle(globalData, article)
        except Exception:
            print("Failed to read article '%s'" % article.BaseName)
            raise

    # Remove invalid articles
    for articleName in list(globalData.articles.keys()):
        if not globalData.articles[articleName].Dates:
            print("Ignoring article (no dates)", articleName)
            del globalData.articles[articleName]

    for article in list(globalData.articles.values()):
        ProcessArticle(globalData, article)

    for article in list(globalData.articles.values()):
        OutputArticleHtml(globalData, article)

    print("Generating indices: main page")
    GenerateArticleIndices(globalData, None)

    for label in globalData.labels:
        print("Generating indices:", label.name)
        GenerateArticleIndices(globalData, label)

    print("Done")


if __name__ == "__main__":
    os.chdir(os.path.join(os.path.realpath(os.path.dirname(__file__)), r"../conf"))
    Generate(False)
