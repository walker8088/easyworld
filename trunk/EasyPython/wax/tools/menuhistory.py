# menuhistory.py

class MenuHistory:
    """ Implements a "menu history".  Hook instance up to a Menu like this:

        hist = MenuHistory(menu, callback=somefunction)

        Whenever hist.Add() is called, an item is added to the history, and
        displayed at the end of the menu associated with it.
        <callback> is a function that is called when one of the history menu
        items is clicked.  It should have the signature " callback(title) ",
        where <title> is the label of the menu item that was clicked.
        <max_items> is the maximum number of items the history section can
        have.  This works like a queue; if more are added, items at the top
        are removed.
    """

    def __init__(self, menu, callback, max_items=10, filename=".menuhistory.txt"):
        self.menu = menu
        self.filename = filename
        self.titles = []
        self.max_items = max_items
        self.callback = callback

        # if we have a "save file", load it
        try:
            self.Load()
        except (IOError, OSError):
            pass

    def Add(self, title):
        self.menu.Append(title, event=self.OnMenuClick)
        # remove older occurrences
        while title in self.titles:
            self.titles.remove(title)
            item = self.menu.GetItem(title)
            self.menu.Delete(item)
        self.titles.append(title)

        while len(self.titles) > self.max_items:
            # remove first menu item
            victim = self.titles[0]
            #id = self.menu.FindItem(victim) # returns an id... un-Waxy!
            item = self.menu.GetItem(victim)    # returns a wx.MenuItem
            self.menu.Delete(item)              # ...and deletes that item
            del self.titles[0]

    def Load(self):
        f = open(self.filename, "r")
        lines = f.readlines()
        f.close()
        for line in lines:
            line = line.rstrip()
            if line:
                self.Add(line)

    def Save(self):
        f = open(self.filename, "w")
        for title in self.titles:
            print >> f, title
        f.close()

    def OnMenuClick(self, event):
        # getting the MenuItem must be done through the id; event.GetEventObject()
        # returns the Frame containing the menu
        id = event.GetId()
        menuitem = self.menu.FindItemById(id)
        # I'd replace all the methods that deal with ids, but apparently
        # they are still necessary in some cases...
        title = menuitem.GetLabel()
        self.callback(title)
