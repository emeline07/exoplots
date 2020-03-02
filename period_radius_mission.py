import pandas as pd
from bokeh import plotting
from bokeh.themes import Theme
from bokeh.io import curdoc
from bokeh.models import NumeralTickFormatter, OpenURL, TapTool
import numpy as np
from bokeh.embed import components

theme = Theme(filename="./exoplots_theme.yaml")
curdoc().theme = theme

# colorblind friendly palette from https://personal.sron.nl/~pault/
# other ideas: https://thenode.biologists.com/data-visualization-with-flying-colors/research/
colors = ['#228833', '#ee6677', '#66ccee', '#aa3377', '#ccbb44', '#4477aa', 
          '#aaaaaa']
markers = ['circle', 'square', 'triangle', 'diamond', 'inverted_triangle']


datafile = 'data/confirmed-planets.csv'

embedfile = '_includes/period_radius_embed.html'
fullfile = '_includes/period_radius.html'

df = pd.read_csv(datafile)

# get rid of the long name with just TESS
df['pl_facility'].replace('Transiting Exoplanet Survey Satellite (TESS)', 'TESS', inplace=True)


plotting.output_file(fullfile, title='Period Radius Plot')

TOOLTIPS = [
    ("Planet", "@planet"),
    ("Period", "@period{0,0[.][0000]}"),
    ("Radius", "@radius{0,0[.][000]}"),
]

fig = plotting.figure(x_axis_type='log', y_axis_type='log', tooltips=TOOLTIPS)
fig.add_tools(TapTool())


missions = ['Kepler', 'K2', 'TESS', 'Other']
# colors = palettes.Category10[len(missions)]

for ii, imiss in enumerate(missions):
    if imiss == 'Other':
        good = ((~np.in1d(df['pl_facility'], missions)) & np.isfinite(df['pl_rade']) & 
                np.isfinite(df['pl_orbper']) & df['pl_tranflag'].astype(bool))
    else:
        good = ((df['pl_facility'] == imiss) & np.isfinite(df['pl_rade']) & 
                np.isfinite(df['pl_orbper']) & df['pl_tranflag'].astype(bool))
    
    alpha = 1. - good.sum()/1000.
    alpha = max(0.2, alpha)
    
    source = plotting.ColumnDataSource(data=dict(
    planet=df['pl_name'][good],
    period=df['pl_orbper'][good],
    radius=df['pl_rade'][good],
    host=df['pl_hostname'][good]
    ))
    print(good.sum())
    
    glyph = fig.scatter('period', 'radius', color=colors[ii], source=source, size=8,
               legend_label=imiss, muted_alpha=0.1, muted_color=colors[ii],
               alpha=alpha, marker=markers[ii], nonselection_alpha=alpha,
               nonselection_color=colors[ii])


url = "https://exoplanetarchive.ipac.caltech.edu/overview/@host"
taptool = fig.select(TapTool)
taptool.callback = OpenURL(url=url)


fig.yaxis.axis_label = 'Radius (Earth Radii)'
fig.yaxis.formatter = NumeralTickFormatter(format='0,0[.][0000]')

fig.xaxis.axis_label = 'Period (days)'
fig.xaxis.formatter = NumeralTickFormatter(format='0,0[.][0000]')

fig.legend.location = 'bottom_right'
fig.legend.click_policy="hide"

fig.title.text = 'Confirmed Transiting Planets'

# XXX: need to add date/credit to this and every plot

plotting.save(fig)

script, div = components(fig)

with open(embedfile, 'w') as ff:
    ff.write(div)
    ff.write(script)


