import numpy as np
from os.path import dirname, join
from scipy.optimize import curve_fit
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
import copy


global s1 
global s3
global s4
global s5

# Load data from csv file
file_input_label = Div(text='Please select a file:')
file_input = FileInput()
time = [0]
current = [0]
def upload_csv_to_server(attr, old, new):
    global s1,s4,s5
    data = base64.b64decode(new).decode('utf-8')
    data = data.split('\r\n')
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
    s4.data = dict(x=time, y=current)
    s5.data = dict(x=time, y=current)

file_input.on_change('value', upload_csv_to_server)

# Initialise data sources
# s1: Original whole range data    s2: Section data            s3: Fitted section data
# s4: Devided whole range data     s5: Fitted wholerange data

s1 = ColumnDataSource(data=dict(x=time, y=current))
s2 = ColumnDataSource(data=dict(x=[], y=[]))
s3 = ColumnDataSource(data=dict(x=[], y=[]))
s4 = ColumnDataSource(data=dict(x=time, y=current))
s5 = ColumnDataSource(data=dict(x=time, y=current))

# Create a plot and style its properties (currently not shown)
p = figure(plot_height=300, plot_width=600, tools="xpan,pan,reset,box_zoom,save", toolbar_location="above",
           x_axis_type="linear", x_axis_location="above",x_range=(time[0],time[-1]),
           background_fill_color="#efefef")
p.line('x', 'y', source=s1)

# Cutting data section with range tools (top-left )
p_select = figure(plot_height=300, plot_width=600, tools="xpan,pan,reset,box_zoom,save",y_range=p.y_range,
                x_axis_type="linear", x_axis_location="above",
                toolbar_location="above", background_fill_color="#efefef")
range_tool = RangeTool(x_range=p.x_range)
range_tool.overlay.fill_color = "navy"
range_tool.overlay.fill_alpha = 0.2

p_select.line('x', 'y', source=s1)
p_select.ygrid.grid_line_color = None
p_select.add_tools(range_tool)
p_select.toolbar.active_multi = range_tool

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
        s3.data = s2.data
        s2.change.emit();
        s3.change.emit();

    """)
range_tool.x_range.js_on_change('start', callback1)
range_tool.x_range.js_on_change('end', callback1)


# Plotting data in range (bottom right)
p2 = figure( plot_height=300,plot_width=600,tools="", title="Watch Here",background_fill_color="#efefef")
p2.line('x', 'y', source=s2, alpha=0.6)
p2.line('x', 'y', source=s3, alpha=0.6)

# Saving data in range
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


# Select fitting function 
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

# Plot data and the fitting function in the top-right plot and divided data in the bottom-left plot
p3 = figure( plot_height=300,plot_width=600,tools="xpan,pan,reset,box_zoom,save", title="Origin&Fit",background_fill_color="#efefef")
p3.line('x', 'y', source=s5, alpha=0.6)
p3.line('x', 'y', source=s1, alpha=0.6)

p4 = figure( plot_height=300,plot_width=600,tools="",toolbar_location="above", title="Divided",background_fill_color="#efefef")
p4.line('x', 'y', source=s4, alpha=0.6)

def update():
    global s3,s4,s5
    function = select_functions()
    print(function(1,1,1,1))
    x3 = s3.data['x']
    y3 = s3.data['y']
    x4 = s4.data['x']
    y5 = copy.deepcopy(s1.data['y'])
    y4 = copy.deepcopy(s1.data['y'])
    popt = []
    print(x4)
    if fittingFunction.value == "None" or len(x3)==0:
        pass
    elif fittingFunction.value == "BaseLinear":
        popt, pcov = curve_fit(function, x3, y3)
        for i in range(len(y3)):
            y3[i] = function(x3[i],*popt)   
        for j in range(len(x4)):
            y5[j] = function(x4[j],*popt)
            y4[j] = y4[j]/function(x4[j],*popt)

    elif fittingFunction.value == "BaseExponential":
        xmin,ymin = min(x3), min(y3)
        x30 = [x - xmin for x in x3]
        y30 = [(y - ymin)*100000 for y in y3]
        popt, pcov = curve_fit(function, x30, y30,maxfev=50000)
        for i in range(len(y3)):
            y3[i] = function(x3[i]-xmin,*popt)/100000 + ymin
        for j in range(len(x4)):
            y5[j] = function(x4[j]-xmin,*popt)/100000 + ymin
            y4[j] = y4[j]/(function(x4[j]-xmin,*popt)/100000 + ymin)

    elif fittingFunction.value == "BaseLogarithmic":
        # Normalize function for improved fitting
        corrX = [x/x3[0] for x in x3]
        corrYFactor = y3[-1]
        corrY = [y/corrYFactor for y in y3]

        popt, pcov = curve_fit(function, corrX, corrY,maxfev=50000)
        for i in range(len(y3)):
            y3[i] = corrYFactor*function(x3[i]/x3[0],*popt)
        for j in range(len(x4)):
            y5[j] = corrYFactor*function(x4[j]/x3[0],*popt)
            y4[j] = y4[j]/(corrYFactor*function(x4[j]/x3[0],*popt))

    elif fittingFunction.value == "BaseFraction":
        # Offset the function for improved fitting
        corrX = [x - x3[0] for x in x3]
        corrYFactor = y3[-1]
        corrY = [y-corrYFactor for y in y3]

        popt, pcov = curve_fit(function, corrX, corrY,maxfev=50000)
        for i in range(len(y3)):
            y3[i] = corrYFactor+function(x3[i]-x3[0],*popt)
        for j in range(len(x4)):
            y5[j] = corrYFactor+function(x4[j]-x3[0],*popt)
            y4[j] = y4[j]/(corrYFactor+function(x4[j]-x3[0],*popt))



    s3.data['y'] = y3
    s4.data['y'] = y4
    s5.data['y'] = y5

controls = [fittingFunction]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

range_tool.x_range.on_change('start', lambda attr, old, new: update())
range_tool.x_range.on_change('end', lambda attr, old, new: update())

# put the button and plot in a layout and add to the document
curdoc().add_root(column(row(column(file_input_label,file_input),fittingFunction),row(p_select,p3),row(p4,p2),savebutton))