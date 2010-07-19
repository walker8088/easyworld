#--------------------------------------------------------------
# img2waxrf.py
#   Purpose: To import images into a waxrf file
#    Author: Jason Gedge
#
#   TODO:
#       - 
#--------------------------------------------------------------


from wax import *
import wax.tools.waxrf.imgcoder as imgcoder
import xml.dom.minidom as minidom
import os


resource_str = '<from resource file>'


class ScrolledImage(Canvas):
    def __init__(self, parent, bmp, *args, **kwargs):
        self.bmp = bmp
        Canvas.__init__(self, parent, *args, **kwargs)

        # Find the smallest dimension and restrict it to (150, 500)
        mindim = min(self.bmp.GetWidth(), self.bmp.GetHeight())
        self.x, self.y = 0, 0
        if mindim < 150:
            mindim = 150
            self.x = (150 - self.bmp.GetWidth()) / 2
            self.y = (150 - self.bmp.GetHeight()) / 2
        elif mindim > 500:
            mindim = 500
        self.size = (mindim, mindim)
        
        self.SetSize(self.size)

    def OnDraw(self, dc):
        dc.DrawBitmap(self.bmp, self.x, self.y)

class PreviewDialog(CustomDialog):
    def __init__(self, parent, bmp):
        self.bmp = bmp
        #self.size = ( min(self.bmp.GetWidth(), 300), min(self.bmp.GetHeight(), 300) )
        CustomDialog.__init__(self, parent, title='Image Preview')

    def Body(self):
        si = ScrolledImage(self, self.bmp)
        si.SetScrollbars(1, 1, self.bmp.GetWidth(), self.bmp.GetHeight())
        
        self.AddComponent(si)
        self.Pack()

class MainFrame(VerticalFrame):
    def __init__(self, *args, **kwargs):
        VerticalFrame.__init__(self, *args, **kwargs)
        self.file = ""
        self.xml = None
        self.xmlimgs = {}

    def Body(self):
        # Create components
        self.fd = FileDialog(self, open=1, default_dir=os.curdir)

        p1 = VerticalPanel(self)

        p3 = HorizontalPanel(p1)
        b4 = Button(p3, text='Select WaxRF...', event=self.doSelect)
        self.lbl1 = Label(p3, noresize=1)

        p2 = HorizontalPanel(p1)
        b2 = Button(p2, text='Add Image', event=self.doAdd)
        b3 = Button(p2, text='Delete Image', event=self.doDelete)

        b1 = Button(p1, text='Import!', event=self.doImport)
        self.lv = ListView(p1, columns=['File', 'Name'], size=(300,200))
        
        # Do stuff with the controls
        self.lv.OnItemDoubleClick = self.doPreview
        b1.Enable(False)
        b2.Enable(False)
        b3.Enable(False)

        # Add components
        p2.AddComponent(b2, border=2)
        p2.AddComponent(b3, border=2)
        p2.Pack()

        p3.AddComponent(b4, border=2)
        p3.AddComponent(self.lbl1, border=5, expand='h')
        p3.Pack()

        p1.AddComponent(p3, border=2, expand='h')
        p1.AddComponent(self.lv, border=3, expand='both')
        p1.AddComponent(p2, border=2, align='c')
        p1.AddComponent(b1, border=2, align='c')
        p1.Pack()

        self.AddComponent(p1, expand='both')
        self.Pack()
        self.Center()

    def doPreview(self, event=None):
        sel = event.GetIndex()
        file, name = self.lv[sel, 0], self.lv[sel, 1]
        if file == resource_str:
            bmp = BitmapFromData(imgcoder.DecodeImage(self.xmlimgs[name]))
        else:
            bmp = BitmapFromFile(file)

        dlg = PreviewDialog(self, bmp)
        dlg.ShowModal()

    def doImport(self, event=None):
        if os.path.exists(self.file):
            self._save_xml(self.file)

    def doAdd(self, event=None):
        if self.fd.ShowModal() == 'ok':
            imgfile = self.fd.GetPath()
            ted = TextEntryDialog(self, title='Add Image', prompt='Enter the reference name for this image')
            if ted.ShowModal() == 'ok':
                name = ted.GetValue().strip()
                if name == '':
                    pass # XXX Error message box here!!!!
                else:
                    self.lv.AppendRow(imgfile, name)
                    # Add the XML node
                    bnode = self.xml.createElement('Image')
                    dnode = self.xml.createTextNode(imgcoder.EncodeImageFile(imgfile))
                    bnode.setAttribute('name', name)
                    bnode.appendChild(dnode)                    
                    self.xml.documentElement.appendChild(bnode)

    def doDelete(self, event=None):
        sel = self.lv.GetSelected()
        sel.reverse()
        names = []
        for x in sel:
            names.append(self.lv[x,1])
            self.lv.DeleteItem(x)

        for node in self.xml.documentElement.childNodes:
            if node.nodeName == 'Image':
                name = node.getAttribute('name')
                if name in names:
                    self.xml.documentElement.removeChild(node)
                    
    def doSelect(self, event=None):
        if self.fd.ShowModal() == 'ok':
            self.file = self.fd.GetPath()
            self._load_xml(self.file)
            self.lbl1.SetLabel(os.path.basename(self.file))

            self.b1.Enable(True)
            self.b2.Enable(True)
            self.b3.Enable(True)

    def _load_xml(self, fname):
        self.lv.DeleteAllItems()
        self.xml = minidom.parse(fname)
        self.xmlimgs = {}
        
        i = 0
        for node in self.xml.documentElement.childNodes:
            if node.nodeName == 'Image':
                name = node.getAttribute('name')
                if name != '':
                    self.lv.AppendRow(resource_str, name)
                    i += 1
                    self.xmlimgs[name] = node.childNodes[0].nodeValue

    def _save_xml(self, fname):
        fout = file(fname, 'w')
        self.xml.writexml(fout)

app = Application(MainFrame, title='WaxRF Image Import Utility')
app.Run()
