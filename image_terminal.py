# image_terminal.py
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, Vte, Gdk

class ImageTerminal(Gtk.Overlay):
    def __init__(self):
        super().__init__()
        image = Gtk.Image.new_from_file("bg.jpg")
        self.add(image)

        self.terminal = Vte.Terminal.new()
        self.add_overlay(self.terminal)

        # Set color of the terminal
        color = Gdk.RGBA(55 / 255, 55 / 255, 55 / 255, 0.9)
        self.terminal.set_color_background(color)

    # Add the update_terminal_colors method
    def update_terminal_colors(self, background_color, foreground_color):
        self.terminal.set_color_background(background_color)
        self.terminal.set_color_foreground(foreground_color)
