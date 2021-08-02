
import numpy as np
import csv
import os
from bokeh.io import save
from bokeh.models import Slider
from bokeh.util.browser import view
from bokeh.io import curdoc
from bokeh.plotting import figure, ColumnDataSource
from bokeh.layouts import row, column
from bokeh.models import Div, ColumnDataSource, CustomJS, FileInput
from bokeh.plotting import figure, save
from bokeh.layouts import column
from bokeh.models import CustomJS, ColumnDataSource, Slider, ranges
from bokeh.plotting import Figure, output_file, show
from bokeh.models import Button  # for saving data
from bokeh.events import ButtonClick  # for saving data
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
from bokeh.models import HoverTool
from bokeh.io import show
from bokeh.models import ColumnDataSource, RangeTool
from bokeh.plotting import figure,curdoc
from bokeh.io import curdoc
from bokeh.models.widgets import FileInput
from base64 import b64decode
import base64


file_input_label = Div(text='Load data file 1')
file_input = FileInput()
time = []
current = []
global s1 

def upload_csv_to_server(attr, old, new):
    global x,y,s1,init_xrange
    #decode base64 format (from python base24 website)
    # base64_message = file_input.value
    # base64_bytes = base64_message.encode('ascii')
    # message_bytes = base64.b64decode(base64_bytes)
    # message = message_bytes.decode('ascii')
    # file = base64.b64decode(new)# .decode('utf-8')
    data = base64.b64decode(new).decode('utf-8')
    data = data.split('\r\n')
    print(data)
    data = data[1:]
    time = []
    current = []
    for row in data:
        row = row.split(",")
        time.append(float(row[0]))
        current.append(float(row[1]))
    print(time)
    print(current)
    s1.data = dict(x=time, y=current)

    

    # with file_input as csvfile:
    #     csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
    #     header = next(csv_reader)  # 读取第一行每一列的标题
    #     for row in csv_reader:  # 将csv 文件中的数据保存到birth_data中
    #         data.append(row)
    #         print(row)

    # data = base64.b64decode(new).decode('utf-8')
    # data = data.split('\r\n')
    # header = data[0].split('\t')
    # print(header)
    # print(data)
    

    # data = b64decode(new)
    #convert string to csv and save it on the server side
    # message_list = data.splitlines()
    

    
    # with data as csv_file:
        # csv_reader = csv.reader(csv_file, delimiter=',')
        # line_count = 0
        # for row in csv_reader:
        #     if line_count == 0:
        #         print(f'Column names are {", ".join(row)}')
        #         line_count += 1
        #     else:
        #         print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
        #         line_count += 1
        # print(f'Processed {line_count} lines.')


# get data

file_input.on_change('value', upload_csv_to_server)

# path = "/Users/apple/Desktop/testdata.csv"
# time,current= np.loadtxt(path,skiprows=1, unpack = True, delimiter = ',',usecols = (0,1))

s1 = ColumnDataSource(data=dict(x=time, y=current))
s2 = ColumnDataSource(data=dict(x=[], y=[]))
# create a plot and style its properties
p = figure(plot_height=600, plot_width=1200, tools="xpan,pan,reset,box_zoom,save", toolbar_location="above",
           x_axis_type="linear", x_axis_location="above",x_range=(0,800),
           background_fill_color="#efefef")
p.line('x', 'y', source=s1)

p_select = figure(title="Drag the middle and edges of the selection box to change the range above",
                plot_height=400, plot_width=1200, tools="xpan,pan,reset,box_zoom,save",y_range=p.y_range,
                x_axis_type="linear", x_axis_location="above",
                toolbar_location="above", background_fill_color="#efefef")

range_tool = RangeTool(x_range=p.x_range)
range_tool.overlay.fill_color = "navy"
range_tool.overlay.fill_alpha = 0.2

p_select.line('x', 'y', source=s1)
p_select.ygrid.grid_line_color = None
p_select.add_tools(range_tool)
p_select.toolbar.active_multi = range_tool

## 1. Cutting data in range
callback1 = CustomJS(args=dict(s1=s1, s2=s2),code="""
        var data1 = s1.data;
        var data2 = s2.data;
        var x1 = data1['x']
        var y1 = data1['y']
        var x2 = data2['x']
        var y2 = data2['y']
        x2.splice(0,x2.length)
        y2.splice(0,y2.length)
        var range_start = cb_obj.start;
        var range_end = cb_obj.end;
        for (var i = 0; i < x1.length; i++) {
            if ((x1[i]< range_end)&&(x1[i]>range_start)){
            x2.push(x1[i])
            y2.push(y1[i])
            } 
        }
        //alert(x2[x2.length-1])
        s2.change.emit();

    """)
range_tool.x_range.js_on_change('start', callback1)
range_tool.x_range.js_on_change('end', callback1)
# Plotting data in range
p2 = figure( plot_height=400,plot_width=800,tools="", title="Watch Here",background_fill_color="#efefef")
p2.line('x', 'y', source=s2, alpha=0.6)

# 2. Saving data in range
savebutton = Button(label="Save Segmented Data", button_type="success")
callback2 = CustomJS(args=dict(s2=s2),code="""
        function table_to_csv(source) {
            const columns = Object.keys(source.data)
            const nrows = source.get_length()
            const lines = [columns.join(',')]

            for (let i = 0; i < nrows; i++) {
                let row = [];
                for (let j = 0; j < columns.length; j++) {
                    const column = columns[j]
                    row.push(source.data[column][i].toString())
                }
                lines.push(row.join(','))
            }
            return lines.join('\\n').concat('\\n')
        }
        const filename = '/Users/apple/Desktop/data_result.csv'
        var filetext = table_to_csv(s2)
        const blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' })

        //addresses IE
        if (navigator.msSaveBlob) {
            navigator.msSaveBlob(blob, filename)
        } else {
            const link = document.createElement('a')
            link.href = URL.createObjectURL(blob)
            link.download = filename
            link.target = '_blank'
            link.style.visibility = 'hidden'
            link.dispatchEvent(new MouseEvent('click'))
        }
                    """)

savebutton.js_on_click(callback2)



#
#range_tool.x_range.js_on_change('start', callback0)
#range_tool.x_range.js_on_change('end', callback0)
# # add a text renderer to the plot (no data yet)
# r = p.text(x=[], y=[], text=[], text_color=[], text_font_size="26px",
#            text_baseline="middle", text_align="center")

# i = 0

# ds = r.data_source

# # create a callback that adds a number in a random location
# def callback():
#     global i

#     # BEST PRACTICE --- update .data in one step with a new dict
#     new_data = dict()
#     new_data['x'] = ds.data['x'] + [random()*70 + 15]
#     new_data['y'] = ds.data['y'] + [random()*70 + 15]
#     new_data['text_color'] = ds.data['text_color'] + [RdYlBu3[i%3]]
#     new_data['text'] = ds.data['text'] + [str(i)]
#     ds.data = new_data

#     i = i + 1

# # add a button widget and configure with the call back
# button = Button(label="Press Me")
# button.on_click(callback)

# put the button and plot in a layout and add to the document
curdoc().add_root(column(file_input,p_select,p2,savebutton))