# waxdocgen.py

import cgi
import cStringIO
import inspect
import pprint
import re
import string
import os, os.path
import shutil

build_data = {
    "application": ["Application"],
    "artprovider": ["ArtProvider"],
    "bitmap": ["Bitmap", "BitmapFromData", "BitmapFromFile"],
    "bitmapbutton": ["BitmapButton"],
    "button": ["Button"],
    "canvas": ["Canvas"],
    "checkbox": ["CheckBox"],
    "checklistbox": ["CheckListBox"],
    "colordb": ["ColorDB"],
    "combobox": ["ComboBox"],
    "containers": ["Container", "GridContainer", "FlexGridContainer",
                   "OverlayContainer", "GroupBoxContainer", "PlainContainer"],
    "customdialog": ["CustomDialog"],
    "dialog": ["Dialog", "showdialog"],
    "directorydialog": ["DirectoryDialog", "ChooseDirectory"],
    "dragdrop": ["FileDropTarget", "TextDropTarget"],
    "dropdownbox": ["DropDownBox"],
    "events": ["events"],
    "filedialog": ["FileDialog"],
    "filetreeview": ["FileTreeView"],
    "findreplacedialog": ["FindReplaceDialog"],
    "flexgridframe": ["FlexGridFrame"],
    "flexgridpanel": ["FlexGridPanel"],
    "font": ["Font"],
    "fontdialog": ["FontDialog"],
    "frame": ["Frame", "HorizontalFrame", "VerticalFrame"],
    "grid": ["Grid"],
    "gridframe": ["GridFrame"],
    "gridpanel": ["GridPanel"],
    "groupbox": ["GroupBox"],
    "htmlwindow": ["HTMLWindow"],
    "image": ["AddImageHandler", "AddAllImageHandlers", "Image", "ImageAsBitmap"],
    "imagelist": ["ImageList"],
    "label": ["Label"],
    "line": ["Line"],
    "listbox": ["ListBox"],
    "listview": ["ListView"],
    "mdiframes": ["MDIChildFrame", "MDIParentFrame"],
    "menu": ["Menu", "MenuBar"],
    "messagedialog": ["MessageDialog", "ShowMessage"],
    "mousepointer": ["MousePointerRegistry"],
    "notebook": ["NoteBook"],
    "overlaypanel": ["OverlayPanel"],
    "panel": ["Panel", "HorizontalPanel", "VerticalPanel"],
    "plainframe": ["PlainFrame"],
    "plainpanel": ["PlainPanel"],
    "radiobutton": ["RadioButton"],
    "scrollframe": ["ScrollFrame"],
    "shell": ["PyCrust", "PyCrustFilling"],
    "simpleeditor": ["SimpleEditor"],
    "sound": ["Sound"],
    "splitter": ["Splitter"],
    "statusbar": ["StatusBar"],
    "styledtextbox": ["StyledTextBox"],
    "taskbaricon": ["TaskBarIcon"],
    "textbox": ["TextBox"],
    "textentrydialog": ["TextEntryDialog"],
    "timer": ["Timer"],
    "togglebutton": ["ToggleButton"],
    "treelistview": ["TreeListView"],
    "treeview": ["TreeView"],
    "utils": ["asstring", "opj"],
}

# wax.core is a special case
import wax.core as core
build_data['core'] = [name for name in dir(core)
                      if not name in ['wx', 'required', 'required_str', 'DEBUG']
                      and not name.startswith("__")]

re_classrepr = re.compile("<class '(.*?)'>")

def span(thing, tag):
    return '<span class="%s">%s</span>' % (tag, thing)

def classnames_from_repr(klass):
    s = repr(klass)
    m = re_classrepr.search(s)
    if m:
        return m.group(1)
    else:
        return klass.__name__ # settle for this

""" Available tags for stylesheet:
- docstring
- function
- method
- moduleindex
- classname
- arglist
- functionname (TBI)
- methodname (TBI)
- value (?)
"""


class HTMLDocWriter:

    def __init__(self, name, title):
        self.f = open("../docs/apidocs/" + name + ".html", "w")
        self.write_header(title)

    def write_header(self, title):
        print >> self.f, "<html>"
        print >> self.f, "<head>"
        # room for title, stylesheet, etc.
        print >> self.f, "<title>", title, "</title>"
        print >> self.f, '<link rel="stylesheet" href="waxapi.css">'
        print >> self.f, "</head>"
        print >> self.f, "<body>"

    def write_footer(self):
        print >> self.f, "</body>"
        print >> self.f, "</html>"

    def write_class_header(self, classname, klass):
        self.beginpara('classheader')
        print >> self.f, "class", span(classname, "classname"), "<br>"
        print >> self.f, "(derives from:",
        mro = [cgi.escape(classnames_from_repr(x))
               for x in inspect.getmro(klass)[1:]]
        mrohtml = string.join(mro, ", ")
        print >> self.f, span(mrohtml, "arglist") + ")", "<br><br>"
        self.write_docstring(klass)
        self.endpara()

    def write_function(self, name, f):
        """ Write a section for a function or method. """
        ismethod = inspect.ismethod(f)
        tag = ismethod and "method" or "function"
        self.beginpara(tag)
        if ismethod:
            args, varargs, varkw, defaults = inspect.getargspec(f.im_func)
        else:
            args, varargs, varkw, defaults = inspect.getargspec(f)
        argnames = args[:]
        if defaults:
            for i in range(len(defaults)):
                value = defaults[i]
                argnames[-(i+1)] = argnames[-(i+1)] + "=" + repr(value)
        if varargs: argnames.append("*" + varargs)
        if varkw: argnames.append("**" + varkw)
        arglist = "(" + string.join(argnames, ", ") + ")"
        print >> self.f, tag, span(name, "functionname"), \
                 span(arglist, "arglist"), "<br>"

        self.write_docstring(f)

        self.endpara()

    def write_docstring(self, thing):
        docstring = getattr(thing, "__doc__")
        if docstring:
            docstring = cgi.escape(string.strip(docstring))
            html = docstring.replace("\n", "<br>")
            # todo: escape characters and stuff...
            x = "<tt>%s</tt>" % (html,)
            print >> self.f, span(x, "docstring")

    def write_blurb(self, name, thing):
        c = cStringIO.StringIO()
        pprint.pprint(thing, c)
        result = cgi.escape(c.getvalue())
        result = result.replace("\n", "<br>")
        self.beginpara()
        print >> self.f, "<tt>", name, "=", result, "</tt>"
        self.endpara()

    def write_intro(self, text):
        print >> self.f, "<h1>", text, "</h1>"

    def beginpara(self, tagname=""):
        if not tagname:
            tag = "<p>"
        else:
            tag = '<p class="%s">' % (tagname,)
        print >> self.f, tag
    def endpara(self):
        print >> self.f, "</p>"
    def close(self):
        self.f.close()


class HTMLIndexWriter:

    def __init__(self):
        self.f = open("../docs/apidocs/waxapidocs.html", "w")
        self.write_header()
        self.colCount = 0

    def write_header(self):
        print >> self.f, "<html>"
        print >> self.f, "<head>"
        # room for title, stylesheet, etc.
        print >> self.f, "<title>", "wax API Documentation", "</title>"
        print >> self.f, '<link rel="stylesheet" href="waxapi.css">'
        print >> self.f, "</head>"
        print >> self.f, "<body>"
        print >> self.f, "<h1> wax API Module Index </h1>"
        print >> self.f, '<table class="moduleindex">'
        print >> self.f, '<tr>'

    def write_footer(self):
        print >> self.f, "</tr>"
        print >> self.f, "</table>"
        print >> self.f, "</body>"
        print >> self.f, "</html>"

    def write_td(self, name):
        print >> self.f, '<td class="moduleindex"><a href="' + name + \
            '.html">' + name + '</a></td>'
        self.colCount += 1
        if self.colCount > 3:
            self.colCount = 0
            self.write_newrow()

    def write_newrow(self):
        print >> self.f, '</tr><tr>'

    def close(self):
        self.f.close()

def main():
    if os.path.exists('../docs/apidocs'):
        filenames = os.listdir('../docs/apidocs')
        for filename in filenames:
            os.remove('../docs/apidocs/' + filename)
    else:
        if not os.path.exists('../docs'):
            os.mkdir('../docs')
        os.mkdir('../docs/apidocs')
    shutil.copy2('waxapi.css', '../docs/apidocs/waxapi.css')
    items = build_data.items()
    items.sort()
    indx = HTMLIndexWriter()
    for modname, names in items:
        print modname
        m = __import__("wax." + modname, {}, {}, ["wax"])

        h = HTMLDocWriter(modname, "module wax/" + modname + ".py")
        # FIXME when we include the tools directory
        h.write_intro("module wax/" + modname + ".py")

        indx.write_td(modname)

        # TODO: module docstring?
        # TODO: stuff in tools directory?

        names.sort()
        for name in names:
            obj = getattr(m, name)

            # figure out what kind of object this is
            if inspect.isclass(obj):
                h.write_class_header(name, obj)

                # print class methods and other attributes...
                for attrname in dir(obj):
                    attr = getattr(obj, attrname)
                    if inspect.ismethod(attr):
                        h.write_function(attrname, attr)
            elif inspect.isfunction(obj):
                h.write_function(name, obj)
            else:
                h.write_blurb(name, obj)

        h.write_footer()
        h.close()
    indx.write_footer()
    indx.close()

if __name__=='__main__':
    main()
