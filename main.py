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
global s2
global s3
global s4
global s5
global s6

# Load data from csv file

file_input_label = Div(text='Please select a file:')
file_input = FileInput(css_classes=["my_fileInput"])
# css to style for the loading button
style = Div(text="""
<style>
::-webkit-file-upload-button {
  background: #e2e2e2;
  color: black;
  position: relative;
  height: 40px;
  width: 110px;
  margin: 0 10px 18px 0;
  text-decoration: none;
  font: 12px "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-weight: bold;
  line-height: 25px;
  text-align: center; 

  -webkit-border-radius: 4px; 
  -moz-border-radius: 4px;
  border-radius: 4px;
}
::-webkit-file-upload-button:hover {
    background: #e2e2e2;
    background: -webkit-gradient(linear, left top, left bottom, from(#e2e2e2), to(#eee));
    background: -moz-linear-gradient(top,  #e2e2e2,  #eee);
}

::-webkit-file-upload-button:visited {
    color: #555;
    border-bottom: 4px solid #b2b1b1;
    text-shadow: 0px 1px 0px #fafafa;
     
    background: #eee;
    background: -webkit-gradient(linear, left top, left bottom, from(#eee), to(#e2e2e2));
    background: -moz-linear-gradient(top,  #eee,  #e2e2e2);
     
    box-shadow: inset 1px 1px 0 #f5f5f5;
}

::-webkit-file-upload-button:after {
    border: 1px solid #cbcbcb;
    border-bottom: 1px solid #a5a5a5;
    content: '';
    position: absolute;
    left: -1px;
    height: 25px;
    width: 80px;
    bottom: -1px;

    -webkit-border-radius: 4px; 
    -moz-border-radius: 4px;
    border-radius: 4px;
}
::-webkit-file-upload-button:before { 
    height: 23px;
    bottom: -4px;
    border-top: 0;

    -webkit-border-radius: 0 0 4px 4px; 
    -moz-border-radius: 0 0 4px 4px;
    border-radius: 0 0 4px 4px;


    -webkit-box-shadow: 0 1px 1px 0px #bfbfbf;
    -moz-box-shadow: 0 1px 1px 0px #bfbfbf;
    box-shadow: 0 1px 1px 0px #bfbfbf;
}

.my_fileInput{
    width: 100px;
	height: 100px;
	
    color: #0d8ba1;
    font-weight:bold !important;
}
</style>
""")
# ::-webkit-file-upload-button {
#   background: #61b93d;
#   color: white;
#   padding: 1em;
#   border-radius: 6px;
# }


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
s6 = ColumnDataSource(data=dict(x=[0,0,0], y=[0,0,0]))

# Create a plot for original data and style its properties (currently not shown)
p = figure(plot_height=300, plot_width=600, tools="xpan,pan,reset,box_zoom,save", toolbar_location="above",
           x_axis_type="linear", x_axis_location="above",x_range=(time[0],time[-1]),
           background_fill_color="#efefef")
p.line('x', 'y', source=s1)

# Plot for cutting data with range tools (top-left )
p_select = figure(plot_height=300, plot_width=600, tools="xpan,pan,reset,box_zoom,save",y_range=p.y_range,
                x_axis_type="linear", x_axis_location="above",title = "Range Selector",
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
p2 = figure( plot_height=300,plot_width=600,tools="", toolbar_location="above",title="Watch Here",background_fill_color="#efefef")
p2.line('x', 'y', source=s2, alpha=0.6)
p2.line('x', 'y', source=s3, alpha=0.6)

# Saving data in range
savebutton = Button(label="Save Segmented Data", button_type="success")
callback2 = CustomJS(args=dict(s2=s2),code="""
        function table_to_csv(source) {
            const columns = ['x','y']
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
        const filename = 'SectionData.csv'
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

# Select if inverting
if_invert = 'Non-inverting'
invert_selector = Select(value=if_invert, title='If invert:', options=['Inverting', 'Non-inverting'])

def invert_plot(attrname, old, new):
    global s1,s2,s3,s4,s5
    s1.data['y'] = [-y for y in s1.data['y']]
    s2.data['y'] = [-y for y in s2.data['y']]
    s3.data['y'] = [-y for y in s3.data['y']]
    s4.data['y'] = [-y for y in s4.data['y']]
    s5.data['y'] = [-y for y in s5.data['y']]

invert_selector.on_change('value', invert_plot)
def update_s2(attr,old,new):
    x1 = copy.deepcopy(s1.data['x'])
    y1 = copy.deepcopy(s1.data['y'])
    x2 = []
    y2 = []
    for i in range(len(s1.data['x'])):
        if x1[i]<range_tool.x_range.end and x1[i]>range_tool.x_range.start:
            x2.append(x1[i])
            y2.append(y1[i])
    s2.data['x'] = x2
    s2.data['y'] = y2
invert_selector.on_change('value', update_s2)

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
p3 = figure( plot_height=300,plot_width=600,tools="xpan,pan,reset,box_zoom,save", toolbar_location="above",title="Origin&Fit",background_fill_color="#efefef")
p3.line('x', 'y', source=s5, alpha=0.6)
p3.line('x', 'y', source=s1, alpha=0.6)

p4 = figure( plot_height=300,plot_width=600,tools="xpan,pan,reset,box_zoom,save",toolbar_location="above", title="Divided",background_fill_color="#efefef")
p4.line('x', 'y', source=s4, alpha=0.6)


def update():
    global s2,s3,s4,s5,s6
    function = select_functions()
    #print(function(1,1,1,1))
    x3 = s3.data['x']
    y3 = s3.data['y']
    x4 = s4.data['x']
    y5 = copy.deepcopy(s1.data['y'])
    y4 = copy.deepcopy(s1.data['y'])
    popt = []
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
        popt, pcov = curve_fit(function, x30, y30,maxfev=100000)
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
    if invert_selector.value == "Inverting":
        y4 = [1-y for y in y4]
    elif invert_selector.value == 'Non-inverting':
        y4 = [y-1 for y in y4]
    abc = copy.deepcopy(popt)
    s3.data['y'] = y3
    s4.data['y'] = y4
    s5.data['y'] = y5
    s6.data['y'] = abc
    print(abc)
    print(s1.data)
    print(s2.data)
controls = [fittingFunction,invert_selector]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

range_tool.x_range.on_change('start',lambda attr, old, new: update())
range_tool.x_range.on_change('end',lambda attr, old, new: update())

# Saving fitting parameters
saveFuncButton = Button(label="Save Fitting Function Parameters", button_type="success")

paramCall = CustomJS(args=dict(s2=s2,fittingFunction=fittingFunction,s6=s6,invert_selector=invert_selector),code="""
        function parameter_to_csv(s2,fittingFunction,abc) {
            lines = []
            console.log(abc)
            row0 = ["if invert","fit type", "a", "b", "c", "x start", "x end"]
            row1 = [invert_selector.value,fittingFunction.value, abc[0],abc[1],abc[2], s2.data['x'][0],s2.data['x'][s2.data['x'].length-1]]
            lines.push(row0.join(','))
            lines.push(row1.join(','))
            return lines.join('\\n').concat('\\n')
        }
        const filename = 'Parameters.csv'
        var filetext = parameter_to_csv(s2,fittingFunction,s6.data['y'])
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
saveFuncButton.js_on_click(paramCall)


# Saving divided data (s4)
saveDividedButton = Button(label="Save Divided Data", button_type="success")
callback4 = CustomJS(args=dict(s4=s4),code="""
        function table_to_csv(source) {
            const columns = ["x","y"]
            console.log(columns)
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
        const filename = 'DividedData.csv'
        var filetext = table_to_csv(s4)
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

saveDividedButton.js_on_click(callback4)



# put the button and plot in a layout and add to the document
curdoc().add_root(column(row(column(file_input_label,column(file_input,style)),invert_selector,fittingFunction),row(p_select,p3),row(p4,p2),savebutton,saveDividedButton,saveFuncButton))