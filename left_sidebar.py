import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gio
from image_terminal import ImageTerminal

class LeftSidebar(Gtk.Box):
    def __init__(self, main_window):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.set_border_width(1)
        self.set_size_request(20, -1)  # set minimum width, -1 for default height
        self.main_window = main_window  # store a reference to the main window


     
      


        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size('automation.png', 24, 24)
        imageSL2 = Gtk.Image.new_from_pixbuf(pixbuf)
        imageSL2.set_margin_top(2)
        imageSL2.set_margin_bottom(2)
        imageSL2.set_margin_start(2)
        imageSL2.set_margin_end(2)
        button2 = Gtk.Button(label="")
        button2.set_size_request(24, 24)
        button2.set_name('custom_image_button')
        button2.set_image(imageSL2)
        button2.set_margin_bottom(4)
        button2.set_halign(Gtk.Align.START)
        button2.connect("clicked", self.on_automation_button_clicked)  # Connect the button to the automation function


    def on_automation_button_clicked(self, widget):
        self.main_window.on_automation_button_clicked(widget)  # Call the main window's automation function

    def get_image_terminal(self):
        return self.image_terminal
