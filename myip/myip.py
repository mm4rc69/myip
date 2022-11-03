# -*- coding: utf-8 -*-
"""My ip main window ui file."""

from pathlib import Path

import gi

gi.require_version(namespace='Gtk', version='4.0')
gi.require_version(namespace='Adw', version='1')

from gi.repository import Adw, Gio, Gtk

Adw.init()

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent.parent
CUSTOM_IMAGE = str(
    ROOT_DIR.joinpath('myip', 'myip', 'data', 'icons', 'com.github.mm4rc69.myip.svg')
)

class myipMainWindow(Gtk.ApplicationWindow):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

        self.set_title(title='My ip info')
        self.set_default_size(width=int(800 / 2), height=int(1000 / 2))
        self.set_size_request(width=int(800 / 2), height=int(1000 / 2))

        headerbar = Gtk.HeaderBar.new()
        self.set_titlebar(titlebar=headerbar)

        menu_button_model = Gio.Menu()
        menu_button_model.append('Preferences', 'app.preferences')
        menu_button_model.append('About', 'app.about')

        menu_button = Gtk.MenuButton.new()
        menu_button.set_icon_name(icon_name='open-menu-symbolic')
        menu_button.set_menu_model(menu_model=menu_button_model)
        headerbar.pack_end(child=menu_button)


class myip(Adw.Application):

    def __init__(self):
        super().__init__(application_id='com.github.mm4rc69.myip',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.create_action('quit', self.exit_app, ['<primary>q'])
        self.create_action('preferences', self.on_preferences_action)
        self.create_action('about', self.on_about_action)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = myipMainWindow(application=self)
        win.present()

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_shutdown(self):
        Gtk.Application.do_shutdown(self)

    def on_preferences_action(self, action, param):
        print('preferences has been actived.')

    def on_about_action(self, action, param):
        dialog = Adw.AboutWindow.new()
        dialog.set_transient_for(parent=self.get_active_window())
        dialog.set_application_name('My ip')
        dialog.set_version('0.0.1')
        dialog.set_developer_name('Marc Michel (mm4rc69)')
        dialog.set_license_type(Gtk.License(Gtk.License.MIT_X11))
        dialog.set_comments('Display information about your IP address')
        dialog.set_website('https://github.com/mm4rc69/myip')
        dialog.set_issue_url("https://github.com/mm4rc69/myip/issues")
        dialog.add_credit_section('Contributors', [''])
        dialog.set_translator_credits('')
        dialog.set_copyright('© 2022 Marc Michel (mm4rc69)')
        dialog.set_developers(['mm4rc69 https://github.com/mm4rc69'])
        dialog.set_application_icon(CUSTOM_IMAGE)
        dialog.present()
        print(CUSTOM_IMAGE)

    def exit_app(self, action, param):
        self.quit()

    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f'app.{name}', shortcuts)


if __name__ == '__main__':
    import sys

    app = myip()
    app.run(sys.argv)
