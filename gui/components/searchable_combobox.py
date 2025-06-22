"""
Searchable Combobox Component
Provides keyboard search functionality for combobox widgets
"""

import tkinter as tk
from tkinter import ttk

class SearchableCombobox:
    @staticmethod
    def make_searchable(combobox, values_list):
        """Make a combobox searchable with keyboard input"""
        def on_keyrelease(event):
            value = event.widget.get()
            if value == '':
                combobox['values'] = values_list
            else:
                filtered = [item for item in values_list if value.lower() in item.lower()]
                combobox['values'] = filtered
        
        combobox.bind('<KeyRelease>', on_keyrelease)
        return combobox
    
    @staticmethod
    def create_searchable_combobox(parent, textvariable, values_list, **kwargs):
        """Create a new searchable combobox"""
        combobox = ttk.Combobox(parent, textvariable=textvariable, **kwargs)
        combobox['values'] = values_list
        SearchableCombobox.make_searchable(combobox, values_list)
        return combobox
