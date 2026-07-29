import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats

# =====================================================
# CONFIGURATION
# =====================================================

draft_year = 2007

# =====================================================
# LOAD DATA
# =====================================================

df = pd.read_csv(
    '/Users/justinmarcelcamonayan/Desktop/Codes/NBA/nba_draft_2007.csv'
)

# =====================================================
# CLEAN DATA
# =====================================================

cols = [
    'Pk',
    'Yrs',
    'G',
    'PTS_per_game',
    'TRB_per_game',
    'AST_per_game',
    'FG%',
    '3P%',
    'FT%',
    'WS'
]


for c in cols:
    df[c] = pd.to_numeric(
        df[c],
        errors='coerce'
    )


df[cols] = df[cols].fillna(0)

# =====================================================
# CAREER PRODUCTION INDEX
# =====================================================

df['Impact_Score'] = (
      df['WS']           * 3.0
    + df['PTS_per_game'] * 1.8
    + df['TRB_per_game'] * 1.4
    + df['AST_per_game'] * 1.7
    + df['Yrs']          * 1.2
    + df['G']            * 0.03
    + df['FG%']          * 18
    + df['3P%']          * 18
    + df['FT%']          * 10
)

# =====================================================
# REGRESSION MODEL
# =====================================================

slope, intercept, r, _, _ = stats.linregress(
    df['Pk'],
    df['Impact_Score']
)


df['Expected'] = (
    (slope * df['Pk']) + intercept
)

df['Residual'] = (
    df['Impact_Score'] - df['Expected']
)



# =====================================================
# PLAYER CATEGORY
# =====================================================

df['Category'] = np.where(
    df['Residual'] > 15,
    'Overperformer',
    np.where(
        df['Residual'] < -15,
        'Underperformer',
        'Expected'
    )
)



color_map = {
    'Overperformer': '#2ecc71',
    'Expected': '#95a5a6',
    'Underperformer': '#e74c3c'
}


df['Color'] = df['Category'].map(color_map)

# =====================================================
# HOVER INFORMATION
# =====================================================

df['Hover'] = (
    "<b>" + df['Player'] + "</b><br>" +
    "Draft Pick: #"
    +
    df['Pk'].astype(int).astype(str)
    +
    "<br>Impact Score: "
    +
    df['Impact_Score'].round(1).astype(str)
    +
    "<br>Expected Score: "
    +
    df['Expected'].round(1).astype(str)
    +
    "<br>Residual: "
    +
    df['Residual'].round(1).astype(str)
    +
    "<br>Category: "
    +
    df['Category']
    +
    "<br>Win Shares: "
    +
    df['WS'].round(1).astype(str)
    +
    "<br>Career Seasons: "
    +
    df['Yrs'].astype(int).astype(str)

)

# =====================================================
# SUMMARY DATA
# =====================================================

avg_score = df['Impact_Score'].mean()


top5_avg = df[
    df['Pk'] <= 5
]['Impact_Score'].mean()


total_ws = df['WS'].sum()


players_analyzed = len(df)



best_late = df[
    df['Pk'] > 14
].loc[

    df[
        df['Pk'] > 14
    ]['Impact_Score'].idxmax()

]


best_player = df.loc[
    df['Impact_Score'].idxmax()
]


biggest_steal = df.loc[
    df['Residual'].idxmax()
]


biggest_bust = df.loc[
    df['Residual'].idxmin()
]



# =====================================================
# TOP 5 PLAYERS
# =====================================================

top5_players = (

    df.sort_values(

        by='Impact_Score',

        ascending=False

    )

    .head(5)

    [
        [
            'Player',
            'Pk',
            'Impact_Score',
            'WS',
            'Yrs'
        ]
    ]

)


top5_players['Impact_Score'] = (
    top5_players['Impact_Score']
    .round(1)
)


top5_players['WS'] = (
    top5_players['WS']
    .round(1)
)



# =====================================================
# CREATE FIGURE
# =====================================================

fig = go.Figure()



# =====================================================
# DRAFT ZONES
# =====================================================

fig.add_vrect(

    x0=1,
    x1=5,

    fillcolor="rgba(220,53,69,0.05)",

    line_width=0

)


fig.add_vrect(

    x0=5,
    x1=14,

    fillcolor="rgba(255,193,7,0.05)",

    line_width=0

)


fig.add_vrect(

    x0=14,
    x1=30,

    fillcolor="rgba(13,110,253,0.04)",

    line_width=0

)



# =====================================================
# PLAYER SCATTER
# =====================================================

fig.add_trace(

    go.Scatter(

        x=df['Pk'],

        y=df['Impact_Score'],

        mode='markers',

        marker=dict(

            color=df['Color'],

            size=12,

            line=dict(

                color='white',

                width=1

            )

        ),

        text=df['Hover'],

        hovertemplate='%{text}<extra></extra>',

        name='Players'

    )

)



# =====================================================
# REGRESSION LINE
# =====================================================

fig.add_trace(

    go.Scatter(

        x=[1,60],

        y=[

            slope * 1 + intercept,

            slope * 60 + intercept

        ],

        mode='lines',

        line=dict(

            color='#e63946',

            width=3

        ),

        name=f'Expected Value Trend (R² = {r**2:.3f})'

    )

)
# =====================================================
# PLAYER LABELS
# =====================================================

fig.add_annotation(

    x=best_player['Pk'],

    y=best_player['Impact_Score'],

    text=f"Best Player<br>{best_player['Player']}",

    showarrow=True,

    arrowhead=2

)


fig.add_annotation(

    x=biggest_steal['Pk'],

    y=biggest_steal['Impact_Score'],

    text=f"Biggest Steal<br>{biggest_steal['Player']}",

    showarrow=True,

    arrowhead=2

)


fig.add_annotation(

    x=biggest_bust['Pk'],

    y=biggest_bust['Impact_Score'],

    text=f"Biggest Bust<br>{biggest_bust['Player']}",

    showarrow=True,

    arrowhead=2

)



# =====================================================
# SUMMARY CARD
# =====================================================

summary_card = f"""

<b>{draft_year} Draft Class Summary</b><br>

━━━━━━━━━━━━━━<br>

<b>Players Analyzed:</b> {players_analyzed}<br>

<b>Average CPI:</b> {avg_score:.1f}<br>

<b>Top-5 Pick Average:</b> {top5_avg:.1f}<br>

<b>Total Career WS:</b> {total_ws:.0f}<br>

<b>Regression R²:</b> {r**2:.3f}<br>

<b>Best Late Pick:</b><br>

{best_late['Player']} 
(#{int(best_late['Pk'])})

"""



fig.add_annotation(

    text=summary_card,

    xref="paper",

    yref="paper",

    x=0,
    y=0.20,

    xanchor="left",

    yanchor="top",

    showarrow=False,

    align="left",

    font=dict(size=14),

    bgcolor="rgba(255,255,255,0.95)",

    bordercolor="#1f2937",

    borderwidth=1.5,

    borderpad=10

)

# =====================================================
# FINAL DASHBOARD LAYOUT
# =====================================================

fig.update_layout(

    title=dict(

        text=(

            f"<b>{draft_year} NBA Draft Class Value Analysis</b><br>"

            "<sup>"

            "Career production compared against draft position expectations"

            "</sup>"

        ),

        x=0.5,

        font=dict(size=24)

    ),


    xaxis=dict(

        title="<b>Draft Pick Number</b>",

        range=[0,61],

        fixedrange=True,

        showgrid=True,

        gridcolor="rgba(0,0,0,0.08)"

    ),


    yaxis=dict(

        title="<b>Career Production Index</b>",

        domain=[0.35,1],

        range=[

            0,

            df['Impact_Score'].max()*1.1

        ],

        fixedrange=True,

        showgrid=True,

        gridcolor="rgba(0,0,0,0.08)"

    ),



    width=1300,
    height=1200,


    plot_bgcolor="#f8f9fa",

    paper_bgcolor="white",


    hoverlabel=dict(

        bgcolor="white",

        font_size=14

    ),

    margin=dict(
        t=120,
        b=50,
        l=50,
        r=50
    ),

    legend=dict(
        x=0.99,
        y=0.99,
        xanchor="right",
        yanchor="top"
    )
)

# =====================================================
# SHOW DASHBOARD
# =====================================================

fig.show()
