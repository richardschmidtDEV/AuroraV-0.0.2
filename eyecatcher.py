import gi
from portscan_eyecatcher import PortScanGUI

from subdomain_eyecatcher import DirectoryGUI, enumerate_directories
from visual_eyecatcher import DirectoryVisualizer
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# (other imports and respective classes: SubdomainGUI, PortScanGUI, VisualEyecatcher)

class MainWindow(Gtk.Window):

    def __init__(self):
        super().__init__(title="Red Team Toolkit")
        self.set_border_width(10)
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)
        
        # Directory Enumeration
        self.directory_gui = DirectoryGUI()
        vbox.pack_start(self.directory_gui, True, True, 0)
        
        # Visualization
        self.visual_eyecatcher = DirectoryVisualizer()
        vbox.pack_start(self.visual_eyecatcher, True, True, 0)
        
        # When directories are enumerated, visualize them
        self.directory_gui.button.connect("clicked", self.directory_enumerated)
        
    def directory_enumerated(self, widget):
        url = self.directory_gui.entry.get_text()
        if url:
            directories = enumerate_directories(url)
            data_for_visual = {dir: [] for dir in directories}
            self.visual_eyecatcher.update_data(data_for_visual)


if __name__ == '__main__':
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
