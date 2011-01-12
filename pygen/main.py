#!/usr/bin/python

import os, sys, re, time, datetime
from warnings import warn
from smartypants import smartyPants
from markdown2 import Markdown
from cache import Cache, SqlBackend
from pytz import timezone, utc
import codecs
import ETL

# TODO: make this a per-article and config thing
defaultTimeZone = timezone('Europe/London')

class GlobalData:
    """A holding structure for global data.  Nicer than global variables."""
    def __init__(self):
        self.config = {}
        self.articles = {}
        self.cache = None
        self.labels = set()

    def GetValue(self, value, label):
        if label:
            labelName = value + "." + label.name
            if labelName in self.config:
                return self.config[labelName]
            wildcardName = value + ".*"
            if wildcardName in self.config:
                return self.config[wildcardName].replace("*", label.filename)
            return ""
        else:
            return self.config.get(value, "")

    def GetInheritedValue(self, value, label):
        if label:
            labelName = value + "." + label.name
            if labelName in self.config:
                return self.config[labelName]
            wildcardName = value + ".*"
            if wildcardName in self.config:
                return self.config[wildcardName].replace("*", label.filename)
            
        return self.config[value]

    def GetInheritedInt(self, value, label):
        return int(self.GetInheritedValue(value, label))

    def GetPublicArticles(self, label):
        if label:
            func = lambda a: a.Status == "public" and label in a.Labels
        else:
            func = lambda a: a.Status == "public"
        return filter(func, self.articles.values())
        
    def SetCache(self, cache):
        self.cache = cache

class Article:
    """An article"""
    def __init__(self, globalData, name):
        self.BaseName = name.replace('\\', '/')
        self.ArticleModified = 0
        self.HtmlModified = 0
        self.Status = "public"
        self.Author = globalData.config["DefaultArticleAuthor"]
        self.LicenseURL = globalData.config["DefaultArticleLicenseURL"]
        self.Dates = []
        self.Labels = []
        self.Summary = ""
        self.Via = ""
        self.ArticleText = ""
        self.HtmlText = ""
        self.XHtmlText = ""
        self.RawTitle = ""
        self.Title = ""
        self.URLPrefix = globalData.config['ArticleURLPrefix']
        self.PrevArticle = None
        self.NextArticle = None
        
    def __getattr__(self, name):
        name = name.lower()
        if name == "title": return self.Title
        elif name == "contenthtml": return self.HtmlText
        elif name == "contentxhtml": return self.XHtmlText
        elif name == "basename": return self.BaseName
        elif name == "summary": return self.Summary
        elif name == "via": return self.Via
        elif name == "basenamename":
            return 'a' + re.sub('[^a-zA-Z0-9.-]', '_', self.BaseName)
        elif name == "datehtml":
            return FormatHtmlDate(self.Dates[0])
        elif name == "dateiso":
            return FormatISODate(self.Dates[0])
        elif name == "datesatom": return FormatAtomDates(self.Dates)
        elif name == "datemonth":
            return self.Dates[0].strftime('%B %Y')
        elif name == "permalink": return self.URLPrefix + self.BaseName
        elif name == "datemonthprev": return self.PrevArticle and self.PrevArticle.DateMonth or ""
        elif name == "labels": return self.Labels
        
        raise AttributeError, "Unknown attribute " + name

class Label:
    """Holds information about a label."""
    def __init__(self, name):
        self.name = name
        self.filename = name.replace(" ", "-")
        
    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def __hash__(self):
        return hash(self.name)
        
    def __repr__(self):
        return "Label(%s)" % self.name

def ReadGeneratorConfig(filename, globalData):
    lineNumber = 0
    
    for line in open(filename, 'r'):
        lineNumber += 1
        line = line.strip()
        # Skip empty lines and comment lines
        if not line or line[0] == '#': continue
        try:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            if key in globalData.config:
                warn("%s:%d : Duplicate key '%s'" % (filename, lineNumber, key))
            globalData.config[key] = value
        except ValueError:
            warn("%s:%d : Missing ':'" % (filename, lineNumber))

def CheckConfig(globalData):
    def IsPresent(key):
        if not key in globalData.config:
            raise Exception, "Missing required configuration option '%s'" % key
    def IsDir(key):
        IsPresent(key)
        if not os.path.isdir(globalData.config[key]):
            raise Exception, "Missing directory '%s' for configuration option '%s'" % (globalData.config[key], key)
    def IsFile(key):
        IsPresent(key)
        if not os.path.isfile(globalData.config[key]):
            raise Exception, "Missing file '%s' for configuration option '%s'" % (globalData.config[key], key)
    def CreateDummy(key, value = ""):
        if not key in globalData.config:
            globalData.config[key] = value
    def IsNumber(key):
        IsPresent(key)
        try:
            value = int(globalData.config[key])
            if value <= 1:
                raise Exception, "Invalid numeric value %d (< 1) for configuration option '%s'" % (value, key)
        except ValueError:
            raise Exception, "Invalid numeric value '%s' for configuration option '%s'" % (globalData.config[key], key)
            
    IsDir("ArticleDirectory")
    IsPresent("ArticleURLPrefix")
    CreateDummy("RenderTitlePipeline")
    CreateDummy("RenderHTMLPipeline")
    CreateDummy("RenderXHTMLPipeline")
    IsFile("ArticleTemplate")
    
    if not CreateDummy("FrontPageTemplate"):
        IsFile("FrontPageTemplate")
        IsPresent("FrontPageArticleCount")
        IsPresent("FrontPageOutput")

    if not CreateDummy("AtomFeedTemplate"):
        IsFile("AtomFeedTemplate")
        IsPresent("AtomFeedArticleCount")
        IsPresent("AtomFeedOutput")

    if not CreateDummy("ArchiveTemplate"):
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
            basename = os.path.join(root, basename)[len(articleDir) + 1:]
            if extension == ".html":
                article = GetArticle(globalData, basename)
                article.HtmlModified = os.path.getmtime(fullPath)
            elif extension == ".text":
                article = GetArticle(globalData, basename)
                article.TextModified = os.path.getmtime(fullPath)
        if ".svn" in dirs:
            dirs.remove(".svn")

def ParseDate(date):
    """Parse date (a string in the format "YYYY-MM-DD[ HH[:MM[:SS]]]"""
    match = re.match(r'\s*(\d\d\d\d)-(\d\d)-(\d\d)(?:\s+(\d\d)(?::(\d\d)(?::(\d\d))?)?)?\s*', date)
    if match:
        year, month, day, hour, minute, second = [int(i or 0) for i in match.groups()]
        local_dt = datetime.datetime(year, month, day, hour, minute, second, 0)
        return defaultTimeZone.localize(local_dt, is_dst=None)
    raise ValueError, 'Invalid date string "' + date + '"'

def ReadArticle(globalData, article):
    processingHeader = True
    filename = os.path.join(globalData.config["ArticleDirectory"], article.BaseName + ".text")
    try:
        fileHandle = codecs.open(filename, 'r', 'utf8')
    except IOError:
        print "Ignoring article '%s' as cannot open" % filename
        return
    article.RawTitle = fileHandle.readline().strip()
    # Strip the BOM, if needed.
    article.RawTitle = article.RawTitle.lstrip(unicode(codecs.BOM_UTF8, 'utf8'))
    print "Read article", article.RawTitle
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
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                if key in headers:
                    warn("%s:%d : Duplicate key '%s'" % (filename, lineNumber, key))
                headers[key] = value
            except ValueError:
                raise Exception, "%s:%d : Missing ':''" % (filename, lineNumber)
        else:
            article.ArticleText += line
    for key, value in headers.items():
        if key == 'status':
            value = value.lower()
            if value not in ['public', 'private', 'draft']:
                raise Exception, "Invalid status: '" + value + "'"
            article.Status = value
        elif key == 'date':
            article.Dates = [ParseDate(val) for val in value.split(',')]
        elif key == 'author':
            article.Author = value
        elif key == 'licenseurl':
            article.LicenseURL = value
        elif key == 'summary':
            article.Summary = value
        elif key == 'via':
            article.Via = value
        elif key == 'label':
            article.Labels = [Label(label.strip()) for label in value.split(",")]
        else:
            raise Exception, "Invalid header: '" + key + "'"
    # Only count labels with public articles.
    if article.Status == "public":
        for label in article.Labels:
            globalData.labels.add(label)
    if not article.Dates:
        raise Exception, "Missing article date(s)"

def ProcessTitle(title):
    title = re.sub('&(?!#)', '&amp;', title)
    title = title.replace('<', '&lt;')
    title = title.replace('>', '&gt;')
    return title

xhtmlToHtmlRe = re.compile(r'(<(hr|br|img|param)[^<>]*)/>')
def XHtmlToHtml(xhtml):
    """As Markdown.py doesn't have the --html4tags option, this is my quick and dirty
    xhtml to html converter."""
    return xhtmlToHtmlRe.sub(r'\1>', xhtml).replace('&nbsp;', '&#160;')

def CleanUpXHtml(xhtml):
    return xhtml.replace('&nbsp;', '&#160;')

def CacheArticle(globalData, article):
    article.Title = ProcessTitle(article.RawTitle)
    cacheObj = (10, article.ArticleText)
    resultObj = globalData.cache.Find(cacheObj)
    if resultObj:
        print "Read cached article", article.RawTitle
        article.XHtmlText, article.HtmlText = resultObj
    else:
        print "Caching article", article.RawTitle
        md = Markdown(extras=["code-color", "footnotes"])
        xhtmlText = smartyPants(md.convert(article.ArticleText), attr="2")
        article.XHtmlText = CleanUpXHtml(xhtmlText)
        article.HtmlText = XHtmlToHtml(xhtmlText)
        globalData.cache.Add(cacheObj, (article.XHtmlText, article.HtmlText))

def FormatHtmlDate(date):
    suffix = "th"
    if date.day in [1, 21, 31]: suffix = "st"
    if date.day in [2, 22]: suffix = "nd"
    if date.day in [3, 23]: suffix = "rd"
    return date.strftime('%X %Z on ' + str(date.day) + '<sup>' + suffix + '</sup> %B %Y')

def FormatISODate(date):
    localDate = date.astimezone(utc)
    return localDate.strftime('%Y-%m-%dT%XZ')

def FormatAtomDates(dates):
    if len(dates) == 1:
        return "<updated>" + FormatISODate(dates[0]) + "</updated>"
    return "<published>" +FormatISODate(dates[0]) + "</published>" + \
           "\n".join(["<updated>" + FormatISODate(date) + "</updated>" for date in dates[1:]])

def GetArticleDict(globalData, article):
    d = dict()
    d['basename'] = article.BaseName
    d['basenameNAME'] = article.BaseNameNAME
    d['title'] = article.Title
    d['status'] = article.Status
    d['summary'] = article.Summary
    d['via'] = article.Via
    d['author'] = article.Author
    d['permalink'] = article.Permalink
    d['contentHTML'] = article.HtmlText
    d['contentXHTML'] = article.XHtmlText
    d['licenseURL'] = article.LicenseURL
    d['dateHTML'] = article.DateHTML
    d['dateISO'] = article.DateISO
    d['dateMonth'] = article.DateMonth
    # TODO: dateMonthPrev
    d['datesAtom'] = article.DatesAtom
    d['year'] = str(datetime.datetime.now().year)
    d['labels'] = article.Labels
    d['allLabels'] = globalData.labels
    
    return d

def GetTemplateDependencies(globalData, template, includePath):
    # See if we have this cached - using the name of the template and its modification time.
    cacheObj = (template, os.path.getmtime(template))
    fileList = globalData.cache.Find(cacheObj)
    if fileList:
        try:
            # Try finding all the mtimes of all the dependencies
            fileList = [os.path.getmtime(file) for file in fileList]
        except IOError:
            fileList = None
    if fileList:
        return fileList
    # If we failed then reconstruct the include, and cache them.
    ignored, fileList = ETL.ProcessIncludes(template, includePath)
    fileList.add(template)
    globalData.cache.Add(cacheObj, fileList)
    # Remember to look up the file times and return those.
    fileList = [os.path.getmtime(file) for file in fileList]
    return fileList

def OutputArticleHtml(globalData, article):
    template = globalData.config['ArticleTemplate']
    articleDirectory = globalData.config['ArticleDirectory']
    articleHtml = os.path.join(articleDirectory, article.BaseName + ".html")
    dictionary = GetArticleDict(globalData, article)
    dependencyTimes = GetTemplateDependencies(globalData, template, '.')
    cacheObj = (dictionary, dependencyTimes)
    result = globalData.cache.Find(cacheObj)
    if result:
        print "Found cached article", article.RawTitle
        html = result
    else:
        print "Processing article", article.RawTitle
        html, deps = ETL.Process(template, '.', dictionary)
        globalData.cache.Add(cacheObj, html)
    
    # See if the existing version we've found is the most up-to-date anyway.
    cacheObj = html
    if os.path.exists(articleHtml):
        expectedModTime = os.path.getmtime(articleHtml)
        if expectedModTime == globalData.cache.Find(cacheObj):
            print "  article is already up to date."
            return

    output = codecs.open(articleHtml, 'w', "utf-8")
    output.write(html)
    output.close()
    globalData.cache.Add(cacheObj, os.path.getmtime(articleHtml))

def MyMax(objects, key):
    """Replacement for max(obj, key) as python 2.4 doens't have it"""
    if not objects:
        raise ValueError, "max() arg is empty"
    maximum = objects[0]
    maximumValue = key(maximum)
    for value in objects[1:]:
        thisValue = key(value)
        if thisValue > maximumValue:
            maximumValue = thisValue
            maximum = value
    return maximum

def OutputArticles(globalData, articles, template, label, outputName):
    latestUpdate = MyMax(articles, key=lambda a: a.Dates[-1]).Dates[-1]
    d = { 
        'year' : str(datetime.datetime.now().year),
        'label' : label,
        'articles' : articles,
        'latestUpdateISO' : FormatISODate(latestUpdate),
        'allLabels' : globalData.labels
        }
    html, deps = ETL.Process(template, '.', d)
    output = codecs.open(outputName, 'w', 'utf-8')
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
    def SortDate(x, y):
        if x.Dates[0] < y.Dates[0]: return 1
        elif x.Dates[0] > y.Dates[0]: return -1
        return 0
    articles.sort(SortDate)
    for i in range(len(articles)):
        if i == 0:
            articles[i].PrevArticle = None
        else:
            articles[i].PrevArticle = articles[i-1]
        if i == len(articles)-1:
            articles[i].NextArticle = None
        else:
            articles[i].NextArticle = articles[i+1]
    
    htmlOutput = globalData.GetValue("FrontPageOutput", label)
    if htmlOutput and htmlTemplate:
        OutputArticles(globalData, articles[:articleCount], htmlTemplate, label, htmlOutput)
        
    atomOutput = globalData.GetValue("AtomFeedOutput", label)
    if atomOutput and atomTemplate:
        OutputArticles(globalData, articles[:feedCount], atomTemplate, label, atomOutput)
        
    archiveOutput = globalData.GetValue("ArchiveOutput", label)
    if archiveOutput and archiveTemplate:
        OutputArticles(globalData, articles, archiveTemplate, label, archiveOutput)

def Generate(forceGenerate):
    globalData = GlobalData()
    ReadGeneratorConfig("../conf/generator.conf", globalData)
    
    CheckConfig(globalData)
    if forceGenerate:
        globalData.config["ForceRefresh"] = True

    # TODO: configurable cache file
    globalData.SetCache(Cache(SqlBackend("pycache.db")))

    ScanArticleDirectory(globalData)

    for article in globalData.articles.itervalues():
        try:
            ReadArticle(globalData, article)
        except Exception:
            print "Failed to read article '%s'" % article.BaseName
            raise
    
    # Remove invalid articles
    for articleName in globalData.articles.keys():
        if not globalData.articles[articleName].Dates:
            print "Ignoring article (no dates)", articleName
            del globalData.articles[articleName]
    
    for article in globalData.articles.values():
        CacheArticle(globalData, article)
        
    for article in globalData.articles.values():
        OutputArticleHtml(globalData, article)
    
    print "Generating indices: main page"
    GenerateArticleIndices(globalData, None)
    
    for label in globalData.labels:
        print "Generating indices:", label.name
        GenerateArticleIndices(globalData, label)

    print "Flushing cache"
    globalData.cache.Flush()
    print "Done"
        
if __name__ == "__main__":
    os.chdir(r'../conf')
    Generate(False)
    
