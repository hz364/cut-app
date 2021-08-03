import numpy as np
from os.path import dirname, join
from bokeh.io import save,curdoc
from bokeh.util.browser import view
from bokeh.plotting import figure, ColumnDataSource
from bokeh.layouts import row, column
from bokeh.models import Div, ColumnDataSource, CustomJS, FileInput, Range1d, RangeTool, Select
from bokeh.layouts import column
from bokeh.models import CustomJS, ColumnDataSource, Slider, ranges
from bokeh.plotting import Figure, output_file, show
from bokeh.models import Button  
import base64

file_input_label = Div(text='Please select a file:')
file_input = FileInput()
time = [0]
current = [0]
global s1 
global s3

def upload_csv_to_server(attr, old, new):
    global x,y,s1,initRange
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
    if len(time)!=0:
        initRange = Range1d(start = time[0],end = time[-1])



# get data

file_input.on_change('value', upload_csv_to_server)

# path = "/Users/apple/Desktop/testdata.csv"
# time,current= np.loadtxt(path,skiprows=1, unpack = True, delimiter = ',',usecols = (0,1))

s1 = ColumnDataSource(data=dict(x=time, y=current))
s2 = ColumnDataSource(data=dict(x=[], y=[]))
s3 = ColumnDataSource(data=dict(x=[], y=[]))
# create a plot and style its properties
p = figure(plot_height=300, plot_width=600, tools="xpan,pan,reset,box_zoom,save", toolbar_location="above",
           x_axis_type="linear", x_axis_location="above",x_range=(time[0],time[-1]),
           background_fill_color="#efefef")
p.line('x', 'y', source=s1)

p_select = figure(title="Drag the middle and edges of the selection box to change the range above",
                plot_height=300, plot_width=600, tools="xpan,pan,reset,box_zoom,save",y_range=p.y_range,
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
callback1 = CustomJS(args=dict(s1=s1, s2=s2, s3=s3),code="""
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
        s3 = s2
        s2.change.emit();
        s3.change.emit();

    """)
range_tool.x_range.js_on_change('start', callback1)
range_tool.x_range.js_on_change('end', callback1)
# Plotting data in range
p2 = figure( plot_height=300,plot_width=600,tools="", title="Watch Here",background_fill_color="#efefef")
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

# Tuesday

fittingFunction = Select(title="FittingFunctions", value="",
               options=open(join(dirname(__file__), 'fitting-functions.txt')).read().split())


def select_functions():
    fittingFunction_val = fittingFunction.value
    selected = None
    # Fitting functions
    # Haifan - Baseline 1
    def BaseLinear(x, a, b, c):
        return a * x + b + c
    # Haifan - Baseline 2
    def BaseExponential( x, a, b, c):
        return a * np.exp(-b * x) + c
    # Haifan - Baseline 3
    def BaseLogarithmic(x, a, b, c):
        return a * np.log(b * x) + c
    # Haifan - Baseline 4
    def BaseFraction(x, a, b, c):
        return a / (1 + b * x) + c
    if (fittingFunction_val == "BaseLinear"):
        selected = BaseLinear
    if (fittingFunction_val == "BaseExponential"):
        selected = BaseExponential
    if (fittingFunction_val == "BaseLogarithmic"):
        selected = BaseLogarithmic
    if (fittingFunction_val == "BaseFraction"):
        selected = BaseFraction
    return selected

def update():
    global s3
    function = select_functions()
    print(function(1,1,1,1))
    # s3.data['y'] = dict(
    #     x=df[x_name],
    #     y=df[y_name],
    #     color=df["color"],
    #     title=df["Title"],
    #     year=df["Year"],
    #     revenue=df["revenue"],
    #     alpha=df["alpha"],
    # )
controls = [fittingFunction]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())




# put the button and plot in a layout and add to the document
curdoc().add_root(column(row(column(file_input_label,file_input),fittingFunction),p_select,p2,savebutton))