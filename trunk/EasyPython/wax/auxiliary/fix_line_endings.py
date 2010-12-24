# fix_line_endings.py
#   Sets line endings of all Wax files to \n (Unix style).
#   Author: Jason Gedge.

import EpyGlob


def fix_newlines(filename):
    """Ensure that lines end with just `\n`"""
    f = open(filename, "r")
    lines1 = f.readlines()
    lines2 = [ line.rstrip('\n\r') + '\n' for line in lines1 ]
    f.close()

    if lines1 != lines2:
        f = open(filename, "wb")
        f.writelines(lines2)
        f.close()

if __name__ == "__main__":

    # Get all files in wax directory and its subdirectories
    files = EpyGlob.EpyGlob('..\\*.py') + EpyGlob.EpyGlob('..\\*\\*.py')

    # Take care of any double newlines
    for file in files:
        print "fixing " + file
        fix_newlines(file)

