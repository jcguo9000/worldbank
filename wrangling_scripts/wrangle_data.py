import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.colors
from collections import OrderedDict
import requests

# default list of all countries of interest: BRICS
# BRICS is the group composed by the five major emerging countries
# Brazil, Russia, India and South Africa

country_default = OrderedDict([('Brazil', 'BRA'), ('Russia', 'RUS'),
                              ('India', 'IND'), ('China', 'CHN'),
                              ('South Africa', 'ZAF')])


def return_figures(countries=country_default):
    """Creates six plotly visualizations using the World Bank API
  # Example of the World Bank API endpoint:
  # GDP in US$ for the United States and China from 1990 to 2015
  # http://api.worldbank.org/v2/countries/usa;chn/indicators/NY.GDP.MKTP.CD?date=1990:2015&format=json
    Args:
        country_default (dict): list of countries for filtering the data
    Returns:
        list (dict): list containing the four plotly visualizations
  """

  # when the countries variable is empty, use the country_default dictionary

    if not bool(countries):
        countries = country_default

  # prepare filter data for World Bank API
  # the API uses ISO-3 country codes separated by ;

    country_filter = list(countries.values())
    country_filter = [x.lower() for x in country_filter]
    country_filter = ';'.join(country_filter)

  # World Bank indicators of interest for pulling data

    indicators = [
        'NY.GDP.MKTP.CD', # GDP (current US$)
        'SP.POP.GROW',	# Population growth (annual %)
        'SP.RUR.TOTL.ZS', #Total rural population
        'AG.LND.FRST.ZS', #Total forested land
        'SI.POV.DDAY', #Poverty headcount ratio at $1.90 a day (2011 PPP) (% of population)
        'NE.EXP.GNFS.ZS',# Export of goods and services (% of GDP)
        'SP.URB.TOTL.IN.ZS',# Urban population (% of total population)
        'TM.VAL.FUEL.ZS.UN',# Fuel import (% of merchandise import)
        ]

    data_frames = []  # stores the data frames with the indicator data of interest
    urls = []  # url endpoints for the World Bank API

  # pull data from World Bank API and clean the resulting json
  # results stored in data_frames variable

    for indicator in indicators:
        url = 'http://api.worldbank.org/v2/countries/' + country_filter \
            + '/indicators/' + indicator \
            + '?date=1990:2015&per_page=1000&format=json'
        urls.append(url)

        try:
            r = requests.get(url)
            data = r.json()[1]
        except:
            print ('could not load data ', indicator)

        for (i, value) in enumerate(data):
            value['indicator'] = value['indicator']['value']
            value['country'] = value['country']['value']

        data_frames.append(data)

  # first chart plots the total GDP from 1990 to 2015 in BRICS countries
  # as a line chart

    graph_one = []
    df_one = pd.DataFrame(data_frames[0])

  # filter values for the visualization
  # df_one.sort_values('value', ascending=False, inplace=True)

  # this country list is re-used by all the charts to ensure legends have the same
  # order and color

    countrylist = df_one.country.unique().tolist().sort()

    for country in countrylist:
        x_val = df_one[df_one['country'] == country].date.tolist()
        y_val = df_one[df_one['country'] == country].value.tolist()
        graph_one.append(go.Scatter(x=x_val, y=y_val,
                         mode='lines+markers', name=country))

    layout_one = dict(title='GDP of BRICS countries from 1990 to 2015',
                      xaxis=dict(title='Year', autotick=False,
                      tick0=1990, dtick=5), yaxis=dict(title='GPD (US$)'
                      ))

  # second chart plots the GDP of all countries in 2015 as a bar chart

    graph_two = []

    df_one = df_one[df_one['date'] == '2015']

    graph_two.append(go.Bar(x=df_one.country.tolist(),
                     y=df_one.value.tolist()))

    layout_two = dict(title='GDP of BRICS Countries in 2015',
                      xaxis=dict(title='Country'),
                      yaxis=dict(title='GPD (US$)'))

  # third chart plots the annual population growth from 1990 to 2015

    graph_three = []
    df_three = pd.DataFrame(data_frames[1])

    for country in countrylist:
        x_val = df_three[df_three['country'] == country].date.tolist()
        y_val = df_three[df_three['country'] == country].value.tolist()
        graph_three.append(go.Scatter(x=x_val, y=y_val,
                           mode='lines+markers', name=country))

    layout_three = \
        dict(title='Annual Population Growth of BRICS countries <br> from 1900 to 2015'
             , xaxis=dict(title='Year', autotick=False, tick0=1990,
             dtick=5), yaxis=dict(title='Percent'))

  # fourth chart shows rural population vs arable land as percents

    graph_four = []
    df_four_a = pd.DataFrame(data_frames[2])
    df_four_a = df_four_a[['country', 'date', 'value']]

    df_four_b = pd.DataFrame(data_frames[3])
    df_four_b = df_four_b[['country', 'date', 'value']]

    df_four = df_four_a.merge(df_four_b, on=['country', 'date'])
    df_four.sort_values('date', ascending=True, inplace=True)

    plotly_default_colors = plotly.colors.DEFAULT_PLOTLY_COLORS

    for (i, country) in enumerate(countrylist):

        current_color = []

        x_val = df_four[df_four['country'] == country].value_x.tolist()
        y_val = df_four[df_four['country'] == country].value_y.tolist()
        years = df_four[df_four['country'] == country].date.tolist()
        country_label = df_four[df_four['country']
                                == country].country.tolist()

        text = []
        for (country, year) in zip(country_label, years):
            text.append(str(country) + ' ' + str(year))

        graph_four.append(go.Scatter(
            x=x_val,
            y=y_val,
            mode='lines+markers',
            text=text,
            name=country,
            textposition='top center',
            ))

    layout_four = \
        dict(title='% of Population that is Rural versus <br> % of Land that is Forested <br> of BRICS countries 1990-2015'
             , xaxis=dict(title='% Population that is Rural', range=[0,
             100], dtick=10),
             yaxis=dict(title='% of Area that is Forested', range=[0,
             100], dtick=10))

	#fifth chart shows the poverty headcount ratio at $1.9 per day (2011 PPP) of total population from 1990 to 2015
			 
    graph_five = []
    df_five = pd.DataFrame(data_frames[4])


    for country in countrylist:
        x_val = df_five[df_five['country'] == country].date.tolist()
        y_val = df_five[df_five['country'] == country].value.tolist()
        graph_five.append(go.Scatter(x=x_val, y=y_val, mode='markers',
                          name=country))

    layout_five = \
        dict(title='Poverty Headcount Ratio at $1.90/day (2011 PPP) <br> of BRICS countries from 1990 to 2015'
             , xaxis=dict(title='Year', autotick=False, tick0=1990,
             dtick=5), yaxis=dict(title='Percent'))
    
	
	
	#sixth chart shows the percentage of the exported service and goods	as the total GDP
	graph_six = []
    df_six = pd.DataFrame(data_frames[5])



    for country in countrylist:
        x_val = df_six[df_six['country'] == country].date.tolist()
        y_val = df_six[df_six['country'] == country].value.tolist()
        graph_six.append(go.Scatter(x=x_val, y=y_val, mode='lines',
                         name=country))

    layout_six = \
        dict(title='Export of Service and Goods (% of GDP) <br> of BRICS countries from 1990 to 2015'
             , xaxis=dict(title='Year', autotick=False, tick0=1990,
             dtick=5), yaxis=dict(title='Percent'))

			 
	#seventh chart shows the percentage of urban population of the total population for these countries from 1990 to 2015			 
    graph_seven = []
    df_seven = pd.DataFrame(data_frames[6])

    for country in countrylist:
        x_val = df_seven[df_seven['country'] == country].date.tolist()
        y_val = df_seven[df_seven['country'] == country].value.tolist()
        graph_seven.append(go.Scatter(x=x_val, y=y_val, mode='lines',
                           name=country))

    layout_seven = \
        dict(title='Urban population (% of total population) <br> of BRICS countries from 1990 to 2015'
             , xaxis=dict(title='Year', autotick=False, tick0=1990,
             dtick=5), yaxis=dict(title='Percent'))

	#eight chart shows the percentage of import fuel as in all the merchandise imported for these countries from 1990 to 2015    
	
	graph_eight = []
    df_eight = pd.DataFrame(data_frames[7])

    for country in countrylist:
        x_val = df_eight[df_eight['country'] == country].date.tolist()
        y_val = df_eight[df_eight['country'] == country].value.tolist()
        graph_eight.append(go.Scatter(x=x_val, y=y_val, mode='lines',
                           name=country))

    layout_eight = \
        dict(title='Fuel imports (% of merchandise imports) <br> of BRICS countries from 1990 to 2015'
             , xaxis=dict(title='Year', autotick=False, tick0=1990,
             dtick=5), yaxis=dict(title='Percent'))

  # append all charts

    figures = []
    figures.append(dict(data=graph_one, layout=layout_one))
    figures.append(dict(data=graph_two, layout=layout_two))
    figures.append(dict(data=graph_three, layout=layout_three))
    figures.append(dict(data=graph_four, layout=layout_four))
    figures.append(dict(data=graph_five, layout=layout_five))
    figures.append(dict(data=graph_six, layout=layout_six))
    figures.append(dict(data=graph_seven, layout=layout_seven))
    figures.append(dict(data=graph_eight, layout=layout_eight))

    return figures
