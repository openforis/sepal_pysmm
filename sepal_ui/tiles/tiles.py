#!/usr/bin/env python3

import sys
sys.path.append('..')

from functools import partial  

from traitlets import HasTraits, link
import ipywidgets as widgets
from ipywidgets.widgets.trait_types import Date, date_serialization

import ipyvuetify as v
import getpass

from sepal_ui import widgetBinding as wb
from sepal_ui import widgetFactory as wf
from sepal_ui import sepalwidgets as s
from sepal_ui import mapping

from sepal_ui.utilities import utils
from modules.ipyfilechooser import FileChooser


def date_picker_tile(Dates):

    import ipywidgets as widgets
    
    def bind_change(change, obj, attr):
        setattr(obj, attr, change['new'])

    # Date unique widget
    w_unique_date = widgets.DatePicker(
        description='Date',
    )
    w_unique_cont = v.Container(
        class_='pa-5 d-none', 
        children=[
            w_unique_date
        ]

    )
    # Create two-way-binding with Dates object
    link((w_unique_date, 'value'), (Dates, 'single_date'))

    # Date range widget
    w_ini_date = widgets.DatePicker(
        description='Start date',
    )
    w_ini_date_cont = v.Container(
        class_='pa-5 d-none', 
        children=[
            w_ini_date
        ]
    )
    link((w_ini_date, 'value'), (Dates, 'start_date'))


    w_end_date = widgets.DatePicker(
        description='End date',
    )
    w_end_date_cont = v.Container(
        class_='pa-5 d-none', 
        children=[
            w_end_date
        ]
    )
    link((w_end_date, 'value'), (Dates, 'end_date'))

    # Selector date method

    w_date_method = v.Select(
        v_model=None,
        label='Retrieve date method', 
        items=['Single date', 'Range', 'All time series']
    )
    
    # Bind the selected value to the object
    w_date_method.observe(partial(bind_change, obj=Dates, attr='date_method'), 'v_model')


    widgets = [w_unique_cont, w_ini_date_cont, w_end_date_cont]

    # Create a behavior after change the clicked value of w_date_method
    wb.bind_dates(w_date_method, widgets, Dates)

    dates_content = v.Layout(
        _metadata={'mount-id': 'data-input'},
        class_="pa-5",
        row=True,
        align_center=True, 
        children=[
            v.Flex(xs12=True, children=[w_date_method]),
            v.Flex(xs12=True, children=[w_unique_cont]),
            v.Flex(xs12=True, children=[
                v.Layout(class_='flex-column', children=[
                    v.Flex(
                        children=[
                            w_ini_date_cont, 
                            w_end_date_cont
                        ])
                    ]
                )
            ])
        ]
    )

    return dates_content

    
def run_process_tile(aoi, dates):
    """ Display the given input values and start de process

    """

    # Instantiate an Output() widget to capture the module outputs.
    # such as stderr or stdout

    out = widgets.Output()
    btn = s.Btn(text="Start")


    # Create an alert element for the process
    process_alert = s.Alert()

    content = v.Layout(
        _metadata={'mount_id': 'aoi_widget'},
        xs12=True,
        row=True,
        class_="ma-5 d-block",
        children=[
            btn,
            process_alert,
            out,
        ])
    wb.bin_pysmm_process(aoi, dates, btn, out, process_alert)
    return content


#create an aoi selector tile with all its bindings
def TileAOI(io, remove_method=[]):
    """render and bind all the variable to create an autonomous aoi selector. It will create a asset in you gee account with the name 'aoi_[aoi_name]'. The assetId will be added to io.assetId.
    
    Args: 
        io (Aoi_IO) : an Aoi_IO object that content all the IO of the aoi selector tile in your app
        remove_method (list) : Remove selection method from default list: 
                                'Country boundaries', 'Draw a shape', 
                                'Upload file', 'Use GEE asset'
        
   Returns:
       tile (v.Layout) : an autonomous tile for AOI selection binded with io
   """

    AOI_MESSAGE='Select the AOI method'
    
    #create the output
    aoi_alert = s.Alert()
    aoi_alert.add_msg(AOI_MESSAGE)

    io.alert = aoi_alert

    selection_method = [
        'Country boundaries', 
        'Draw a shape', 
        'Upload file', 
        'Use GEE asset'
    ]

    if all(method in selection_method for method in remove_method):
        selection_method = list(set(selection_method)^set(remove_method))
    else:
        raise ValueError(f'The selected method does not exist')


    
    # Create input widgets

    aoi_file_input = v.Select(
        items=utils.get_shp_files(), 
        label='Select a file', 
        v_model=None,
        class_='d-none'
    )
    wb.bind(aoi_file_input, io, 'file_input')
    
    # For shapefile
    aoi_file_name = v.TextField(
        label='Select a filename', 
        v_model=io.file_name,
        class_='d-none'
    )
    wb.bind(aoi_file_name, io, 'file_name')
    
    # For country 
    aoi_country_selection = v.Select(
        items=[*utils.create_FIPS_dic()], 
        label='Country/Province', 
        v_model=None,
        class_='d-none'
    )
    wb.bind(aoi_country_selection, io, 'country_selection')
    
    # For GEE Asset

    aoi_asset_name = v.TextField(
        class_='pa-5 d-none mr-10', 
        v_model=io.assetId
    )
    wb.bind(aoi_asset_name, io, 'assetId')

    asset_btn = s.Btn(text = 'Use asset', visible=False, small=True)
    
    w_field = v.Select(
        v_model=io.field, 
        class_='pa-5 d-none', 
        label='Select field...')

    wb.bind(w_field, io, 'field')

    w_column = v.Select(
        v_model=io.column, 
        class_='pa-5 d-none', 
        label='Select variable...'
    )
    # Bind the first widget with the object and create event on second widget
    wb.mbind(w_column, w_field, io, 'column')

    widget_list = [aoi_file_input, aoi_file_name, aoi_country_selection, 
                    aoi_asset_name, asset_btn, w_column, w_field]
    
    #create the map 
    
    m = mapping.SepalMap()
    dc = m.get_drawing_controls()

    wb.handle_draw(dc, io, 'drawn_feat')

    # Bind the w_field and stablish the behavior when changed
    wb.field_map_bind(w_field, io, 'field', m, dc)
    
    #bind the input to the selected method 
    aoi_select_method = v.Select(items=selection_method, label='AOI selection method', v_model=None)
    wb.bindAoiMethod(aoi_select_method, widget_list, io, m, dc, selection_method, aoi_alert)
       
    #assemble everything on a tile 
    inputs = v.Layout(
        _metadata={'mount-id': 'data-input'},
        class_="pa-5",
        row=True,
        align_center=True, 
        children=[
            v.Flex(xs12=True, children=[aoi_select_method]),
            v.Flex(xs12=True, children=[aoi_country_selection]),
            v.Flex(xs12=True, children=[aoi_file_input]),
            v.Flex(xs12=True, children=[aoi_file_name]),
            v.Flex(xs12=True, children=[
                v.Layout(class_='flex-column', children=[
                    v.Flex(xs12=True, 
                        class_='d-inline-flex align-baseline', 
                        children=[
                            aoi_asset_name, 
                            asset_btn
                        ]),
                    v.Flex(
                        children=[
                            w_column, 
                            w_field
                        ])
                    ]
                )
            ]),
            v.Flex(xs12=True, children=[aoi_alert]),
        ]
    )

    AOI_content_main =  v.Layout(
        xs12=True,
        row=True,
        class_="ma-5 d-inline",
        children=[
            v.Card(
                class_="pa-5",
                raised=True,
                xs12=True,
                children=[
                    v.Html(xs12=True, tag='h2', children=['AOI selection']),
                    v.Layout(
                        row=True,
                        xs12=True,
                        children=[
                            v.Flex(xs12=True, md6=True, children=[inputs]),
                            v.Flex(class_="pa-5", xs12=True, md6=True, children=[m])
                        ]
                    )    
                ]
            )
        ]
    )
    
    return AOI_content_main