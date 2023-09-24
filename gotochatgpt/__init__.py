# For more info visit the article https://theawless.github.io/How-to-write-plugins-for-gedit/

# This file needs to be placed like ~/.local/share/gedit/plugins/example/__init__.py
# or renamed like ~/.local/share/gedit/plugins/example.py depending on .plugin file

from gi.repository import GObject, Gtk, Gdk, GLib, Gedit, PeasGtk, Gio
import os
import pathlib 
from .conffile import load_conf_dict
from .libchatgpt import chatgpt_query

textview_textbuffer = None;

def working_over_text(mytext,dict_conf,action_name,api_key):
    myquery='';
    for cmd in dict_conf['commands']:
        if cmd['name']==action_name:
            myquery=cmd['query'];
    result=chatgpt_query(myquery+mytext,api_key);
    return result;

# For our example application, this class is not exactly required.
# But we had to make it because we needed the app menu extension to show the menu.
class GoToChatGPTAppActivatable(GObject.Object, Gedit.AppActivatable):
    app = GObject.property(type=Gedit.App)
    __gtype_name__ = "GoToChatGPTAppActivatable"

    def __init__(self):
        GObject.Object.__init__(self)
        self.menu_ext = None;
        self.menu_item = None;

        # path of conf file
        self.conf_path=os.path.join(pathlib.Path.home(),'GoToChatGPT.json');
        self.dict_conf = load_conf_dict(self.conf_path);
    
    def do_activate(self):
        self._build_menu()

    def _build_menu(self):
        # Get the extension from tools menu        
        self.menu_ext = self.extend_menu("tools-section")
        # This is the submenu which is added to a menu item and then inserted in tools menu.        
        sub_menu = Gio.Menu();

        for dat in self.dict_conf['commands']:
            #                                (label,name)
            sub_menu_item = Gio.MenuItem.new(dat['summary']+'\t'+dat['accelerator'],'win.'+dat['name']);
            sub_menu.append_item(sub_menu_item);
        
        self.menu_item = Gio.MenuItem.new_submenu("Go To ChatGPT", sub_menu)
        self.menu_ext.append_menu_item(self.menu_item)

        for dat in self.dict_conf['commands']:
            # Setting accelerators, now our action is called when Ctrl+Alt+1 is pressed.
            self.app.set_accels_for_action('win.'+dat['name'], [dat['accelerator']]);

    def do_deactivate(self):
        self._remove_menu()

    def _remove_menu(self):
        # removing accelerator and destroying menu items
        self.app.set_accels_for_action("win.dictonator_start", ())
        self.menu_ext = None
        self.menu_item = None


class GoToChatGPTWindowActivatable(GObject.Object, Gedit.WindowActivatable, PeasGtk.Configurable):
    window = GObject.property(type=Gedit.Window)
    __gtype_name__ = "GoToChatGPTWindowActivatable"

    def __init__(self):
        GObject.Object.__init__(self)
        # This is the attachment we will make to bottom panel.
        self.bottom_bar = Gtk.VBox()
        global textview_textbuffer
        textview_textbuffer = None;

        # path of conf file
        self.conf_path=os.path.join(pathlib.Path.home(),'GoToChatGPT.json');
        self.dict_conf = load_conf_dict(self.conf_path);

    #this is called every time the gui is updated
    def do_update_state(self):
        # if there is no document in sight, we disable the action, so we don't get NoneException
        if self.window.get_active_view() is not None:
            for dat in self.dict_conf['commands']:
                self.window.lookup_action(dat['name']).set_enabled(True)

    def do_activate(self):
        # Defining the action which was set earlier in AppActivatable.
        self._connect_menu()
        self._insert_bottom_panel()

    def _connect_menu(self):
        for dat in self.dict_conf['commands']:
            action = Gio.SimpleAction(name=dat['name'])
            action.connect('activate', self.action_command)
            self.window.add_action(action)

    def action_command(self, action, data):
        global textview_textbuffer
        mytext=self._get_selected_text();
        if mytext!=None:
            result=working_over_text(mytext,self.dict_conf,action.get_name(),self.dict_conf['api_key']);
            textview_textbuffer.set_text(result);

    def _insert_bottom_panel(self):
        global textview_textbuffer
        textview_panel = Gtk.TextView()
        textview_panel.set_top_margin(10);
        textview_panel.set_right_margin(10);
        textview_panel.set_bottom_margin(10);
        textview_panel.set_left_margin(10);
        
        #textview_panel.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(62535, 62535, 62535))
        textview_textbuffer = textview_panel.get_buffer()
        textview_textbuffer.set_text("This is some text inside of a Gtk.TextView. ")

        # Add elements to panel.
        self.bottom_bar.add(textview_panel)

        # Get bottom bar (A Gtk.Stack) and add our bar.        
        panel = self.window.get_bottom_panel()
        panel.add_titled(self.bottom_bar, 'examplepanel', "Output ChatGPT")
        # Make sure everything shows up.
        panel.show()
        self.bottom_bar.show_all()
        panel.set_visible_child(self.bottom_bar)

    def do_deactivate(self):
        self._remove_bottom_panel()

    def _remove_bottom_panel(self):
        panel = self.window.get_bottom_panel()
        panel.remove(self.bottom_bar)

    ## preferences->plugins->nameplugin->preferences
    def do_create_configure_widget(self):
       
        # Just return your box, PeasGtk will automatically pack it into a box and show it.
        box=Gtk.VBox()
        #
        label1=Gtk.Label();  
        label1.set_markup('<b>Configure file</b>:');
        box.add(label1);
        box.add(Gtk.Label(self.conf_path))
        #
        label2=Gtk.Label();  
        label2.set_markup('<b>API Key</b>:');
        box.add(label2);
        box.add(Gtk.Label(self.dict_conf['api_key']))
        return box
    
    # get the selectd text
    def _get_selected_text(self):
        view = self.window.get_active_view()
        if view:
            buffer = view.get_buffer()
            text = buffer.get_text(buffer.get_start_iter(),
                                   buffer.get_end_iter(),
                                   include_hidden_chars=True)
            selected_text = buffer.get_selection_bounds()
            if selected_text:
                start, end = selected_text
                selected_text = buffer.get_text(start, end, True)
                #print("Texto seleccionado: ", selected_text)
                return selected_text;
            else:
                print("No se ha seleccionado ningún texto.")
                return None;
        else:
            print("No hay una vista activa en la ventana actual.")
            return None;



class GoToChatGPTViewActivatable(GObject.Object, Gedit.ViewActivatable):
    __gtype_name__ = "GoToChatGPTViewActivatable"

    view = GObject.property(type=Gedit.View)

    def __init__(self):
        GObject.Object.__init__(self)
        # path of conf file
        self.conf_path=os.path.join(pathlib.Path.home(),'GoToChatGPT.json');
        self.dict_conf = load_conf_dict(self.conf_path);

    def do_activate(self):
        #print("Plugin created for", self.view)
        self.view.translate_view_activatable = self
        self.popup_handler_id = self.view.connect('populate-popup', self.populate_popup)
        
    def do_deactivate(self):
        print("Plugin stopped for", self.view)

    def do_update_state(self):
        # Called whenever the view has been updated
        print("Plugin update for", self.view)
        
    def populate_popup(self, view, popup):
        if not isinstance(popup, Gtk.MenuShell):
            return
        
        item = Gtk.SeparatorMenuItem()
        item.show()
        popup.append(item)

        for dat in self.dict_conf['commands']:
            item = Gtk.MenuItem.new_with_mnemonic(dat['summary']);
            item.set_sensitive(self.is_enabled());
            item.show();
            funcs = lambda i,j=dat['name']: self.working_callback(i,view.get_buffer(),j);
            item.connect('activate', funcs);
            popup.append(item);
        
    def working_callback(self,item,document,action_name):
        global textview_textbuffer
        start, end = document.get_selection_bounds();
        mytext = document.get_text(start, end, False);

        newtext=working_over_text(mytext,self.dict_conf,action_name,self.dict_conf['api_key']);
        #print(newtext);
        textview_textbuffer.set_text(newtext);

    def is_enabled(self):
        document = self.view.get_buffer()
        if document is None:
            return False

        start = None
        end = None

        try:
            start, end = document.get_selection_bounds()

        except:
            pass

        return start is not None and end is not None