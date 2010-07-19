"""
Set the wallpaper with APOD, EPOD or NGPOD
by henrysting            2009-01-31
"""
import ctypes
import calendar
import urllib
import socket
import os
import time 
import Image

STOREDIR = os.path.expanduser("~") + '/wallpaper/'
DOWNLOADED = 0
TYPE = 1  #""" 1:Astronomy POD, 2:Earth Science POD, 3:National Geographic POD"""

def setWallPaper(imagePath):
    if os.name=="nt":
        """Given a path to an image, convert it to bmp and set it as wallpaper"""
        bmpImage = Image.open(imagePath)
        newPath = STOREDIR + 'mywallpaper.bmp'
        bmpImage.save(newPath, "BMP")
        setWallpaperFromBMP(newPath)
    elif os.name=="posix": 
        try:
            os.system("gconftool-2 -t string -s /desktop/gnome/background/picture_filename \""+imagePath+"\" -s /desktop/gnome/background/picture_options stretched")
        except:
            os.system("dcop kdesktop KBackgroundIface setWallpaper \""+imagePath+"\" 7") 

def getPicture():
    if TYPE == 1:
        siteurl = 'http://apod.nasa.gov/apod/'
        sock = urllib.urlopen(siteurl)
        htmlSource = sock.read()
        sock.close()    
        pos1 = htmlSource.find('href="image/')
        pos2 = htmlSource.find('jpg">')
        page2 = htmlSource[pos1+6:pos2+3]
        filename = htmlSource[pos1+17:pos2+3]
        fileurl = siteurl+page2
    elif TYPE == 2:
        siteurl = 'http://epod.usra.edu/'
        sock = urllib.urlopen(siteurl)
        htmlSource = sock.read()
        sock.close()    
        pos1 = htmlSource.find('<A HREF= "archive/images/')
        pos2 = htmlSource.find('.jpg" TARGET="_window">')
        page2 = htmlSource[pos1+10:pos2+4]
        filename = htmlSource[pos1+25:pos2+4]
        fileurl = siteurl+page2
    elif TYPE == 3:
        siteurl = 'http://photography.nationalgeographic.com'
        sock = urllib.urlopen("http://lava.nationalgeographic.com/cgi-bin/pod/PhotoOfTheDay.cgi")
        htmlSource = sock.read()
        sock.close()    
        pos1 = htmlSource.find('Enlarge</a>')
        pos2 = htmlSource.find('Wallpaper</a>')
        page2 = htmlSource[pos1+50:pos2-2]
        pageurl = siteurl+page2
        print pageurl
        sock = urllib.urlopen(pageurl)
        htmlSource = sock.read()
        sock.close()    
        pos1 = htmlSource.find('art-icon-wallpaper-1280.gif')
        pos2 = htmlSource.find('1280 x 1024 pixels')
        page2 = htmlSource[pos1+42:pos2-2]
        fileurl = siteurl+page2
        filename = page2[page2.rfind("/")+1:];
        print "filename=", filename
    else:
        print 'Wrong Type!'
        
    try:    
        print filename
        print fileurl
        fname = STOREDIR + filename
        if not os.path.exists(fname):
            print 'file not retrieved'
            urllib.urlretrieve(fileurl, fname)
            print 'got the picture from ' + fileurl
        else:
            print 'The file is retrieved'
        return fname
    except Error:
        print "fail to getting picture of ",yy,mm,dd
        pass
    return fname 

def setWallpaperFromBMP(imagepath):  
    SPI_SETDESKWALLPAPER = 20 # According to http://support.microsoft.com/default.aspx?scid=97142  
    ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, imagepath , 0) #SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE  
    #win32gui.SystemParametersInfo(SPI_SETDESKWALLPAPER,imagepath , 0)

def setWallpaperOfToday():
    filename  = getPicture()
    print 'the filename is ' + filename
    setWallPaper(filename) 

def prepare():
    #prepare the directory
    if not os.path.exists(STOREDIR):
        print 'going to make dir ' + STOREDIR
        os.makedirs(STOREDIR)
    print 'prepare done ...' 

prepare()
setWallpaperOfToday() 

print 'Wallpaper set ok!' 
