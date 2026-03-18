#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

WALLPAPER_DIR = Path.home() / "Pictures"
CACHE_DIR = Path.home() / ".cache" / "wallpapers"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

class WallpaperSelector(Gtk.Window):
    def __init__(self):
        super().__init__(title="Обои")
        self.set_default_size(500, 400)
        self.set_decorated(True)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_keep_above(True)
        self.set_resizable(False)
        
        wallpapers = self.get_wallpapers()
        
        grid = Gtk.FlowBox()
        grid.set_selection_mode(Gtk.SelectionMode.NONE)
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        grid.set_max_children_per_line(3)
        
        for wp in wallpapers[:12]:
            thumb = self.create_thumbnail(wp)
            if thumb:
                button = Gtk.Button()
                button.set_relief(Gtk.ReliefStyle.NONE)
                
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(thumb, 150, 100)
                image = Gtk.Image.new_from_pixbuf(pixbuf)
                
                button.set_image(image)
                button.set_always_show_image(True)
                button.set_size_request(150, 100)
                button.connect("clicked", self.on_wallpaper_clicked, wp)
                grid.add(button)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(grid)
        self.add(scroll)
        self.load_css()
        self.connect("key-press-event", self.on_key_press)
    
    def get_wallpapers(self):
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.webp']
        wallpapers = []
        for ext in extensions:
            wallpapers.extend(WALLPAPER_DIR.glob(ext))
            wallpapers.extend(WALLPAPER_DIR.glob(ext.upper()))
        return sorted(wallpapers)[:20]
    
    def create_thumbnail(self, wallpaper_path):
        thumb_path = CACHE_DIR / f"{wallpaper_path.stem}.png"
        
        if not thumb_path.exists():
            try:
                subprocess.run([
                    'convert', str(wallpaper_path),
                    '-resize', '300x200^',
                    '-gravity', 'center',
                    '-extent', '300x200',
                    str(thumb_path)
                ], check=True, capture_output=True)
            except Exception as e:
                print(f"Ошибка создания превью: {e}")
                return None
        
        return str(thumb_path)
    
    def on_wallpaper_clicked(self, button, wallpaper_path):
        subprocess.run(['pkill', '-9', 'swaybg'], capture_output=True)
        subprocess.Popen([
            'swaybg',
            '-m', 'fill',
            '-i', str(wallpaper_path)
        ], start_new_session=True)
        
        self.destroy()
    
    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()
    
    def load_css(self):
        css = b"""
        window {
            background-color: rgba(30, 30, 46, 0.95);
            border-radius: 10px;
        }
        button {
            background-color: transparent;
            border: 2px solid rgba(100, 100, 150, 0.3);
            border-radius: 8px;
            padding: 0px;
        }
        button:hover {
            border-color: rgba(150, 150, 255, 0.8);
            background-color: rgba(100, 100, 200, 0.3);
        }
        image {
            border-radius: 6px;
        }
        scrolledwindow {
            background-color: transparent;
        }
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

if __name__ == "__main__":
    win = WallpaperSelector()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
