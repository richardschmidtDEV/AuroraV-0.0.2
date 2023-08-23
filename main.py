import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from mainwindow import MainWindow

win = MainWindow()
win.connect("delete-event", Gtk.main_quit)
Gtk.main()
