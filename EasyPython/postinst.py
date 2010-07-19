
import sys, os

if sys.platform.startswith('win'):
    platform = 'win'
else:
    platform = 'other'

from distutils.sysconfig import get_python_lib
python_lib = get_python_lib()

EasyPython_base = os.path.join(python_lib, 'EasyPython')
EasyPython_prg = os.path.join(EasyPython_base, 'EasyPython.pyw')
EasyPython_docs = os.path.join(EasyPython_base, 'documentation')
EasyPython_help = os.path.join(EasyPython_docs, 'help.html')

def install():
    """Routine to be run with the -install switch."""

    try:
        import wx
        wx = True
    except ImportError:
        print 'EasyPython needs wxPython (http://www.wxpython.org)'
        wx = False

    if platform == 'win': # Windows specific part of installation

        if wx:
            # here, you could add a wx dialog asking the user:
            # - shall desktop shortcuts be created?
            # - shall start menu shortcuts be created?
            # - user or system wide installation?
            #   (i.e use personal desktop or common desktop, etc.)
            # - take over old user profile? (in case of update, default yes)
            # - associate .py/.pyw extension with EasyPython automatically?
            # - start EasyPython automatically after installation?
            # - show release information after installation?
            # - some fundamental preferences to be preconfigured?
            #   (default language, like tabs or no tabs etc.)
            pass # not yet implemented

        # for the time being, we only add desktop shortcuts (if they do not already exist)

        def create_shortcut_safe(target, description, filename, *args, **kw):
            """Create and register a shortcut only if it doesn't already exist."""
            if not os.path.isfile(filename):
                create_shortcut(target, description, filename, *args, **kw)
                file_created(filename)

        desktop = get_special_folder_path('CSIDL_DESKTOPDIRECTORY')

        create_shortcut_safe(EasyPython_prg,
            'EasyPython Editor/Environment', desktop + '\\EasyPython.lnk')
        create_shortcut_safe(EasyPython_help,
            'EasyPython Online Help', desktop + '\\EasyPython Help.lnk')

def remove():
    """Routine to be run with the -remove switch."""
    pass

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '-install':
            install()
        elif sys.argv[1] == '-remove':
            remove()
