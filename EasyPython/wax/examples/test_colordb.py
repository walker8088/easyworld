# test_colordb.py

from wax import *

cdb = ColorDB()

print "Alles is rood:", cdb['red'], cdb['RED'], cdb['Red']

peachpuff = cdb.byname("peachpuff")
print peachpuff
print cdb.invert(peachpuff)

print "Colors close to peachpuff:"
for x in cdb.findcolors(peachpuff, 20):
    print x

print
colors = ['red', 'yellow', 'papayawhip']
print "Some colors:"
for color in colors:
    print color, cdb[color], cdb.hex(color)

print "Blending:"
print "red and yellow:",
z = cdb.blend('red', 'yellow')
print z
print "Name of this color according to the database:",
closest = cdb.findcolors(z, 1)
print closest[0][1]

print "2 parts red and 1 part yellow:",
z = cdb.blend_weighed('red', 2, 'yellow', 1)
print z
print "Name of this color according to the database:",
closest = cdb.findcolors(z, 1)
print closest[0][1]

print "1 part red and 2 parts yellow:",
z = cdb.blend_weighed('red', 1, 'yellow', 2)
print z
print "Name of this color according to the database:",
closest = cdb.findcolors(z, 1)
print closest[0][1]
