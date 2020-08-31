#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import ipyvuetify as v
from traitlets import HasTraits, Unicode, List, observe


class SepalWidget(v.VuetifyWidget):
    
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        self.class_ = "mt-5"
    
    def hide(self):
        
        if not 'd-none' in self.class_:
            self.class_ = self.class_.strip() + ' d-none'
        
    def show(self):
        
        if 'd-none' in self.class_:
            self.class_ = self.class_.replace('d-none', '')

class Alert(v.Alert, SepalWidget):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.children = ['']
        self.type = 'info'
        self.text = True
        self.clear()
    
    def add_msg(self, msg, type_='info'):
        self.show()
        self.type = type_
        self.children = [msg]
        
    def clear(self):
        self.hide()
        self.children = ['']


class Btn(v.Btn, SepalWidget):
    """
    Creates a process button filled with the provided text
    
    Returns: 
        btn (v.Btn) :
    """
    

    def __init__(self, text='Button', icon=None, visible=True, **kwargs):
        super().__init__(**kwargs)
        self.color='primary'
        
        if icon:
            self.children=[self.set_icon(icon), text]
        else:
            self.children=[text]

        if not visible:
            self.hide()



    def set_icon(self, icon):

        common_icons = {
            'default' : 'mdi-adjust',
            'download' : 'mdi-download'
        }
        
        if not icon in common_icons.keys():
            icon = 'default'
        
        return v.Icon(left=True, children=[common_icons[icon]])    

    def disable(self):
        self.disabled = True
        
    def activate(self):
        self.loading = False
        self.disabled = False
        
    def on_loading(self):
        self.loading = True


class VueDataFrame(v.VuetifyTemplate):
    """
    Vuetify DataTable rendering of a pandas DataFrame
    
    Args:
        data (DataFrame) - the data to render
        title (str) - optional title
    """

    from pandas import DataFrame
    headers = List([]).tag(sync=True, allow_null=True)
    items = List([]).tag(sync=True, allow_null=True)
    search = Unicode('').tag(sync=True)
    title = Unicode('DataFrame').tag(sync=True)
    index_col = Unicode('').tag(sync=True)
    template = Unicode('''
        <template>
          <v-card>
            <v-card-title>
              <span class="title font-weight-bold">{{ title }}</span>
              <v-spacer></v-spacer>
                <v-text-field
                    v-model="search"
                    append-icon="mdi-magnify"
                    label="Search ..."
                    single-line
                    hide-details
                ></v-text-field>
            </v-card-title>
            <v-data-table
                :headers="headers"
                :items="items"
                :search="search"
                :item-key="index_col"
                :footer-props="{'items-per-page-options': [5, 20, 40]}"
            >
                <template v-slot:no-data>
                  <v-alert :value="true" color="error" icon="mdi-alert">
                    Sorry, nothing to display here :(
                  </v-alert>
                </template>
                <template v-slot:no-results>
                    <v-alert :value="true" color="error" icon="mdi-alert">
                      Your search for "{{ search }}" found no results.
                    </v-alert>
                </template>
                <template v-slot:items="rows">
                  <td v-for="(element, label, index) in rows.item"
                      @click=cell_click(element)
                      >
                    {{ element }}
                  </td>
                </template>
            </v-data-table>
          </v-card>
        </template>
        ''').tag(sync=True)
    
    def __init__(self, *args, 
                 data=DataFrame(), 
                 title=None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        
        from json import loads
        data = data.reset_index()
        self.index_col = data.columns[0]
        headers = [{
              "text": col,
              "value": col
            } for col in data.columns]
        headers[0].update({'align': 'left', 'sortable': True})
        self.headers = headers
        self.items = loads(
            data.to_json(orient='records'))
        if title is not None:
            self.title = title