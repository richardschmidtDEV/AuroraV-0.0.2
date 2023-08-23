import gi
from stegano import lsb
import wave
import os

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class SteganoTools:

    @staticmethod
    def hide_in_image(image_path, message, output_path):
        secret = lsb.hide(image_path, message)
        secret.save(output_path)

    @staticmethod
    def reveal_from_image(image_path):
        return lsb.reveal(image_path)

    # Below is a very basic steganography for audio. It works with '.wav' files.
    @staticmethod
    def hide_in_audio(audio_path, message, output_path):
        audio = wave.open(audio_path, mode='rb')
        frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))
        
        # Append dummy data to fill out remaining bytes
        message += int((len(frame_bytes)-(len(message)*8*8))/8) *'#'
        bits = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8,'0') for i in message])))
        
        # Replace LSB of each byte of the audio data
        for i, bit in enumerate(bits):
            frame_bytes[i] = (frame_bytes[i] & 254) | bit
        
        # Write bytes to a new wave file
        with wave.open(output_path, 'wb') as fd:
            fd.setparams(audio.getparams())
            fd.writeframes(frame_bytes)

    @staticmethod
    def reveal_from_audio(audio_path):
        audio = wave.open(audio_path, mode='rb')
        frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))
        extracted = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]
        message = "".join(chr(int("".join(map(str, extracted[i:i+8])), 2)) for i in range(0, len(extracted), 8))
        return message.split('###')[0]



class SteganoGUI(Gtk.Box):

    def __init__(self):
        super().__init__(spacing=10, orientation=Gtk.Orientation.VERTICAL)  # Set orientation to vertical
        self.init_components()

    def init_components(self):

        # Image section
        self.label_image = Gtk.Label()
        self.label_image.set_markup("<b>Image Steganography</b>")
        self.label_image.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1.0, 0.5, 0.0, 1.0))  # Orange color
        self.label_image.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.0, 0.0, 0.0, 0.8))  # Transparent background

        self.file_chooser = Gtk.FileChooserButton.new("Choose a file", Gtk.FileChooserAction.OPEN)
        self.msg_entry = Gtk.Entry()
        self.msg_entry.set_placeholder_text("Enter message or path for the stegano file")

        self.hide_image_button = Gtk.Button(label="Hide in Image")
        self.hide_image_button.connect("clicked", self.hide_in_image)

        self.reveal_image_button = Gtk.Button(label="Reveal from Image")
        self.reveal_image_button.connect("clicked", self.reveal_from_image)

        # Audio section
        self.label_audio = Gtk.Label()
        self.label_audio.set_markup("<b>Audio Steganography</b>")
        self.label_audio.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1.0, 0.5, 0.0, 1.0))  # Orange color
        self.label_audio.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.0, 0.0, 0.0, 0.8))  # Transparent background

        self.hide_audio_button = Gtk.Button(label="Hide in Audio")
        self.hide_audio_button.connect("clicked", self.hide_in_audio)

        self.reveal_audio_button = Gtk.Button(label="Reveal from Audio")
        self.reveal_audio_button.connect("clicked", self.reveal_from_audio)

        self.reveal_file_chooser = Gtk.FileChooserButton.new("Choose a file for revealing", Gtk.FileChooserAction.OPEN)

        # Result display
        self.result_label = Gtk.Label("Output will be displayed here...")
        self.result_label.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.0, 0.0, 0.0, 0.8))  # Transparent background

        # Pack everything with labels
        widgets = [
            self.label_image, self.file_chooser, self.msg_entry,
            self.hide_image_button, self.reveal_image_button,
            self.label_audio,  # Move label_audio widget here
            self.hide_audio_button, self.reveal_audio_button,
            self.reveal_file_chooser, self.result_label
        ]

        for widget in widgets:
            widget.set_margin_top(10)
            widget.set_margin_bottom(10)
            widget.set_margin_start(10)
            widget.set_margin_end(10)
            self.pack_start(widget, False, True, 0)


    def ensure_file_extension(self, path, default_extension=".png"):
        """Ensure the given path has a file extension. If not, add the default one."""
        if not os.path.splitext(path)[1]:  # If there's no file extension
            return path + default_extension
        return path

    def hide_in_image(self, widget):
        input_path = self.file_chooser.get_filename()
        message = self.msg_entry.get_text()
        output_path = input("Enter path for the output image: ")
        
        # Ensure the output path has a file extension
        output_path = self.ensure_file_extension(output_path, ".png")
        
        SteganoTools.hide_in_image(input_path, message, output_path)
        self.result_label.set_text(f"Data hidden in {output_path}")


    def reveal_from_image(self, widget):
        input_path = self.reveal_file_chooser.get_filename()
        if not input_path:
            self.result_label.set_text("Please select a file first.")
            return

        try:
            revealed = SteganoTools.reveal_from_image(input_path)
            self.result_label.set_text(f"Revealed Message: {revealed}")
        except Exception as e:
            self.result_label.set_text(f"Error: {str(e)}")


    def hide_in_audio(self, widget):
        input_path = self.file_chooser.get_filename()
        message = self.msg_entry.get_text()
        output_path = input("Enter path for the output audio: ")
        
        # Ensure the output path has a file extension, assuming .mp3 as default for audio
        output_path = self.ensure_file_extension(output_path, ".mp3")
        
        SteganoTools.hide_in_audio(input_path, message, output_path)
        self.result_label.set_text(f"Data hidden in {output_path}")

    def reveal_from_audio(self, widget):
            input_path = self.reveal_file_chooser.get_filename()
            try:
                revealed = SteganoTools.reveal_from_audio(input_path)
                self.result_label.set_text(f"Revealed Message: {revealed}")
            except Exception as e:
                self.result_label.set_text(f"Error: {str(e)}")


if __name__ == '__main__':
    # Add some custom styling
    style_provider = Gtk.CssProvider()
    css_str = """
    button.suggested-action {
        background-color: #4CAF50;
        border-radius: 5px;
        color: white;
    }
    button.suggested-action:hover {
        background-color: #45a049;
    }
    """
    style_provider.load_from_data(css_str.encode('utf-8'))

    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        style_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    win = Gtk.Window(title="Steganography Tools")
    win.set_default_size(400, 300)
    win.connect("destroy", Gtk.main_quit)
    stegano_gui = SteganoGUI()
    win.add(stegano_gui)
    
    # Set the transparent background with an alpha value of 0.8
    rgba = Gdk.RGBA()
    rgba.parse("rgba(0, 0, 0, 0.3)")
    win.override_background_color(Gtk.StateFlags.NORMAL, rgba)
    
    win.show_all()
    Gtk.main()
