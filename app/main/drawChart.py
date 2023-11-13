import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Color palette for chart drawing which prepared 10 colors
COLOR=['darkturquoise','orange','green','red','blue','brown','violet','magenta','gray','black']

# 2023.11.1 The chart drawing function using the plotly as a library
# Draw chart!!
def line_charts(x_data,y_data,start,points,legend):
    # fig=go.Figure()    
    fig = make_subplots(
        # rows=2, cols=1,
        rows=1, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.2,
        specs=[[{"secondary_y": True}]]
        # specs=[[{"type": "scatter"}]]
        # specs=[[{"type": "scatter"}], [{"type": "scatter"}]]
    )
    
    fig.update_layout(
        title='直近30分(*30)間のデータ推移',
        grid=dict(
            rows=1,
            columns=1,
            pattern='independent',
            roworder='top to bottom',
        ),
        
        xaxis=dict(
            title='時間経過[minutes]',
            showline=True,
            showgrid=True,
            zeroline=True,
            showticklabels=True,
            linecolor='rgb(204,204,204)',
            linewidth=2,
            ticks='outside',
            tickcolor='rgb(204,204,204)',
            tickwidth=2,
            ticklen=5,
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82,82,82)',
            )  
        ),
            
        yaxis=dict(
            title='温度[℃]',
            showline=True,
            showgrid=True,
            zeroline=False,
            showticklabels=True,
            linecolor='rgb(204,204,204)',
            linewidth=2,
            autoshift=True,
            ticks='outside',
            tickcolor='rgb(204,204,204)',
            tickwidth=2,
            ticklen=5,
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82,82,82)',
            )  
        ),
        
        # xaxis2=dict(
        #     title='時間経過[minutes]',
        #     showline=True,
        #     showgrid=True,
        #     zeroline=True,
        #     showticklabels=True,
        #     linecolor='rgb(204,204,204)',
        #     linewidth=2,
        #     ticks='outside',
        #     tickcolor='rgb(204,204,204)',
        #     tickwidth=2,
        #     ticklen=5,
        #     tickfont=dict(
        #         family='Arial',
        #         size=12,
        #         color='rgb(82,82,82)',
        #     )  
        # ),
        
        yaxis2=dict(
            title='圧力[Pa]',
            showline=True,
            showgrid=True,
            zeroline=False,
            showticklabels=True,
            linecolor='rgb(204,204,204)',
            linewidth=2,
            autoshift=True,
            ticks='outside',
            tickcolor='rgb(204,204,204)',
            tickwidth=2,
            ticklen=5,
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82,82,82)',
            )  
        ),        
        
        hovermode='closest',
        autosize=True,
        showlegend=True,
        legend=dict(
            x=0.02,
            y=1.16,
            xanchor='left',
            yanchor='top',
            orientation='h',
        )
    )
    """_summary_ グラフ描画
        左軸：温度[℃]、マーカー● と 右軸：温度以外(以下のところ圧力[Pa]を準備)。
        マーカー■の2軸描画の色分けは9色のみ。
        Returns:
        _type_: _description_
    """
    for i in range(0, points):
        # 温度 [℃]軸        
        if('[℃]' in str(legend[i])):
            fig.add_trace(
                go.Scatter(
                    x = x_data,
                    # y=y_data[start + i],
                    y = y_data[i],   
                    name = str(legend[i]),        # legend table
                    mode = 'lines+markers',
                    connectgaps = True,
                    line = dict(
                        color = COLOR[i],         # color palette
                        width = 2,
                    ),
                    line_dash = 'solid',          # 
                    marker = dict(
                        symbol = 'circle',
                        color = COLOR[i],         # color palette
                        size = 10,
                    ),
                )
            )
        # 圧力軸
        else:
            fig.add_trace(
                go.Scatter(
                    x = x_data,
                    y = y_data[i],
                    # name='trace'+str(i+1),      
                    name = '右軸: ' + str(legend[i]),   # legend table
                    mode = 'lines+markers',
                    connectgaps = True,
                    line = dict(
                        color = COLOR[i],             # color pallet
                        width = 2,
                    ),
                    line_dash = 'solid',
                    marker = dict(
                        symbol = 'square',
                        color = COLOR[i],             # color pallet
                        size = 10,
                    ),   
                ),
                secondary_y = True,
            )
    
    return fig.to_html(include_plotlyjs='cdn',full_html=False).encode().decode('unicode-escape')