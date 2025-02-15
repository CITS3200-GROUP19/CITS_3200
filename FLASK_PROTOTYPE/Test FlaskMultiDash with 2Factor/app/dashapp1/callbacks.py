from datetime import datetime as dt
import pandas_datareader as pdr
from dash.dependencies import Input
from dash.dependencies import Output
import os
import pandas as pd
import plotly.graph_objs as go
import numpy as np
from app.models import FactTable, ReliabilityTable, DefectTable, EyeTable


def label(varX,x_value):
    if varX == "Runtime":
        return str(int(str(x_value)[0:2])) +" to "+ str(int(str(x_value)[0:2])+1)+" Minutes"
    elif varX == "Mean_Deviation":
        return "Between "+ str(10*int(x_value)) + " to " + str(10*int(x_value)+10)
    elif varX == "Pattern_Deviation":
        return "Between "+ str(5*int(x_value)) + " to " + str(5*int(x_value)+5)
    elif varX == "Age":
        return "Between "+ str(10*int(x_value)) + " to " + str(10*int(x_value)+10)
    else:
        return str(x_value)


# from sqlalchemy import create_engine
# PW = os.environ.get('DB_PASSWORD')
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:'+PW+'@localhost/Dashgang'
# db_connection = create_engine(SQLALCHEMY_DATABASE_URI)

# Use df = pd.read_sql(query.statement, query.session.bind)
# or df = pd.read_sql_query(query.statement, engine)
def register_callbacks(dashapp):
    from app.extensions import db

    @dashapp.callback(Output('my-graph', 'figure'), [Input('my-dropdown-Y', 'value'),Input('my-dropdown-X', 'value')])
    def update_graph(varY,varX):
        print(varX,varY)

        #sql_string = 'SELECT * FROM FactTable JOIN ReliabilityTable ON FactTable.ReliabilityID = ReliabilityTable.ReliabilityID JOIN EyeTable ON FactTable.EyeID = EyeTable.EyeID JOIN DefectTable ON DefectTable.DefectID = FactTable.DefectID'
        #df = pd.read_sql(sql_string, con=db.engine)

        query = db.session.query(FactTable,ReliabilityTable,EyeTable,DefectTable).join(ReliabilityTable).join(EyeTable).join(DefectTable)
        df = pd.read_sql(query.statement, con=db.engine)
        print("new",list(df.columns) )
        print("varX",df[varX].dtypes)

        #BINNING
        if (varX == "Age" or varX == "Mean_Deviation"):
            df[varX] = df[varX]//10
        elif varX == "Pattern_Deviation":
            df[varX] = df[varX]//5
        elif varX == "Runtime":
            df[varX] = pd.to_datetime(df[varX], format='%H:%M:%S').dt.minute
        #print(df[varX])
        df = df.sort_values(by=[varX])
        traces = []
        for x_value in eval("df."+varX+".unique()"):
            #LABLES
            labels = label(varX,x_value)

            traces.append(go.Box(y=df[df[varX] == x_value][varY],name=labels,marker={"size": 4},showlegend=False))

            #'colorscale': 'Viridis'}))
        return {"data": traces,
                "layout": go.Layout(autosize=True,
                                    margin={"l": 200, "b": 30, "r": 200,"t": 0},xaxis={"showticklabels": True},
                                    yaxis={"title": varY},
                                    height=400)
                }

    @dashapp.callback(Output('bar-chart', 'figure'), [Input('my-dropdown-Y', 'value'),Input('my-dropdown-X', 'value')])
    def update_graph(varY,varX):
        print(varX,varY)


        if (varX == "Age" or varX == "Mean_Deviation"):
            sql_string = 'SELECT FLOOR('+varX+'/10) AS '+varX+', COUNT('+varX+') FROM FactTable JOIN ReliabilityTable ON FactTable.ReliabilityID = ReliabilityTable.ReliabilityID JOIN EyeTable ON FactTable.EyeID = EyeTable.EyeID JOIN DefectTable ON DefectTable.DefectID = FactTable.DefectID GROUP BY FLOOR('+varX+'/10)'
        elif (varX == "Pattern_Deviation"):
            sql_string = 'SELECT FLOOR('+varX+'/5) AS '+varX+', COUNT('+varX+') FROM FactTable JOIN ReliabilityTable ON FactTable.ReliabilityID = ReliabilityTable.ReliabilityID JOIN EyeTable ON FactTable.EyeID = EyeTable.EyeID JOIN DefectTable ON DefectTable.DefectID = FactTable.DefectID GROUP BY FLOOR('+varX+'/5)'
        elif (varX == "Runtime"):
            sql_string = 'SELECT MINUTE('+varX+') AS '+varX+', COUNT('+varX+') FROM FactTable JOIN ReliabilityTable ON FactTable.ReliabilityID = ReliabilityTable.ReliabilityID JOIN EyeTable ON FactTable.EyeID = EyeTable.EyeID JOIN DefectTable ON DefectTable.DefectID = FactTable.DefectID GROUP BY MINUTE('+varX+')'
        else:
            sql_string = 'SELECT '+varX+', COUNT('+varX+') FROM FactTable JOIN ReliabilityTable ON FactTable.ReliabilityID = ReliabilityTable.ReliabilityID JOIN EyeTable ON FactTable.EyeID = EyeTable.EyeID JOIN DefectTable ON DefectTable.DefectID = FactTable.DefectID GROUP BY '+varX

        df = pd.read_sql(sql_string, con=db.engine)
        df['labels'] = df[varX].apply(lambda x: label(varX,x))
        print(df)
        print(df.groupby(varX).size())

        #'color': df[df[varX] == x_value]['COUNT('+varX+")"].value()
        traces = [go.Bar(x = [label(varX,x_value)], y=df[df[varX]==x_value]['COUNT('+varX+")"],name=label(varX,x_value),marker={
                                                               'colorscale': 'Viridis','line':{'width':1}},showlegend=False, opacity=0.6) for x_value in df[varX]]
        return {"data": traces,
                "layout": go.Layout(title=varX,autosize=True,yaxis={"title": "Counts of "+varX},
                                    margin={"l": 200, "b": 200, "r": 200,"t": 30},
                                    height=400)
        }
