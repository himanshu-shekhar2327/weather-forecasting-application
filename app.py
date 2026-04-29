import sys
sys.path.append('src')

import streamlit as st
from datetime import datetime, timedelta
from predictor import forecast_city
from zones import get_city_info, get_zone_from_coordinates
import streamlit.components.v1 as components
import plotly.graph_objects as go
from apscheduler.schedulers.background import BackgroundScheduler

# ─── PAGE CONFIG ───────────────────────────────────────
st.set_page_config(
    page_title = "WeatherCast India",
    page_icon  = "⛅",
    layout     = "centered"
)

# ─── CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    #MainMenu  {visibility: hidden;}
    footer     {visibility: hidden;}
    header     {visibility: hidden;}

    .stApp {
        background-color: #0D1B3E;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 500px;
        margin: 0 auto;
    }

    /* input wrapper background */
    div[data-testid="stTextInput"] > div > div {
        background-color: rgba(255,255,255,0.85) !important;
        border-radius: 30px !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }

    div[data-testid="stTextInput"] > div > div:focus-within {
        border: 1px solid rgba(100,150,255,0.6) !important;
        box-shadow: none !important;
    }

    /* input text — dark so readable on light background */
    .stTextInput > div > div > input,
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextInput"] > div > div > input {
        background-color: transparent !important;
        background: transparent !important;
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 12px 20px !important;
        font-size: 15px !important;
        caret-color: #111111 !important;
        box-shadow: none !important;
    }

    /* placeholder text */
    div[data-testid="stTextInput"] input::placeholder {
        color: rgba(0,0,0,0.45) !important;
        -webkit-text-fill-color: rgba(0,0,0,0.45) !important;
    }

    /* remove outer wrapper border */
    div[data-testid="stTextInput"] > div {
        border: none !important;
        box-shadow: none !important;
    }

    /* selectbox styling */
    div[data-testid="stSelectbox"] > div > div {
        background-color: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 12px !important;
        color: white !important;
    }

    /* buttons */
    .stButton button {
        background: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 20px !important;
    }
    .stButton button:hover {
        background: rgba(100,150,255,0.3) !important;
    }

    /* tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255,255,255,0.05) !important;
        border-radius: 12px !important;
        padding: 4px !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: rgba(255,255,255,0.6) !important;
        border-radius: 8px !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(100,150,255,0.3) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────────────────
# remembers user search between reruns
if 'city' not in st.session_state:
    st.session_state.city = None
if 'forecast' not in st.session_state:
    st.session_state.forecast = None
if 'coordinates' not in st.session_state:
    st.session_state.coordinates = None

# ─── BACKGROUND SCHEDULER ──────────────────────────────
if 'scheduler_started' not in st.session_state:
    from scheduler import nightly_job
    _scheduler = BackgroundScheduler()
    _scheduler.add_job(nightly_job, 'cron', hour=0, minute=0)
    _scheduler.start()
    st.session_state.scheduler_started = True

# ─── TIME BASED THEME ──────────────────────────────────
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

ist = ZoneInfo('Asia/Kolkata')
now = datetime.now(ist)
hour = now.hour
current_time = now.strftime('%A, %I:%M %p')
if 5 <= hour < 12:
    greeting = "Good morning"
    bg_color  = "#C8510A"
elif 12 <= hour < 17:
    greeting = "Good afternoon"
    bg_color  = "#8B1A00"
elif 17 <= hour < 21:
    greeting = "Good evening"
    bg_color  = "#0D1B3E"
else:
    greeting = "Good night"
    bg_color  = "#050D1A"

# ═══════════════════════════════════════════════════════
# LANDING PAGE
# ═══════════════════════════════════════════════════════
if st.session_state.city is None:

    # app title
    st.markdown("""
    <div style="text-align:center; padding: 2rem 0 1rem;">
        <div style="font-size:48px; margin-bottom:0.5rem;">⛅</div>
        <h1 style="color:white; font-size:28px; 
                   font-weight:600; margin:0;">
            WeatherCast India
        </h1>
        <p style="color:rgba(255,255,255,0.5); 
                  font-size:13px; margin:4px 0 0;
                  letter-spacing:0.1em;">
            STATISTICAL · ML · DEEP LEARNING
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ghost temperature
    st.markdown("""
    <p style="font-size:120px; font-weight:700; 
              color:rgba(255,255,255,0.05);
              text-align:center; margin:0; 
              line-height:1;">30°</p>
    <p style="color:rgba(255,255,255,0.2); font-size:11px;
              text-align:center; letter-spacing:0.15em; 
              margin:0 0 1rem;">
        YOUR CITY, PREDICTED
    </p>
    <hr style="border:none; border-top:0.5px solid rgba(255,255,255,0.1); 
               margin:0 0 1rem;">
    """, unsafe_allow_html=True)

    # ─── SEARCH WITH SUGGESTIONS ───────────────────────
    city_input = st.text_input(
        label            = "Search city",
        placeholder      = "🔍  Try: Mumbai, Puri, Leh...",
        label_visibility = "collapsed"
    )

    # show suggestions when user types 3+ characters
    if city_input and len(city_input) >= 3:
        from fetch_data import get_all_coordinates
        with st.spinner(""):
            suggestions = get_all_coordinates(city_input)

        if suggestions:
            # show dropdown with city + state
            options = [f"{r['name']}, {r['state']}" 
                       for r in suggestions]

            selected = st.selectbox(
                "Select city",
                options,
                label_visibility = "collapsed"
            )

            if st.button("Get Forecast →", use_container_width=True):
                chosen = suggestions[options.index(selected)]
                st.session_state.city = chosen['name']
                st.session_state.coordinates = {
                    'lat': chosen['latitude'],
                    'lon': chosen['longitude'],
                    'alt': chosen.get('elevation', 0)
                }
                st.rerun()

        else:
            st.markdown("""
            <div style="background:rgba(255,80,80,0.15);
                        border:1px solid rgba(255,80,80,0.3);
                        border-radius:12px; padding:12px;
                        text-align:center; margin-top:0.5rem;">
                <p style="color:#FF8080; margin:0; font-size:13px;">
                    ❌ City not found. Try adding state name.<br>
                    <span style="font-size:12px; opacity:0.8;">
                        Example: "Puri, Odisha" or "Leh, Ladakh"
                    </span>
                </p>
            </div>
            """, unsafe_allow_html=True)

    # ─── POPULAR CITIES ────────────────────────────────
    st.markdown("""
    <p style="color:rgba(255,255,255,0.4); 
              font-size:11px; letter-spacing:0.08em;
              margin: 1.5rem 0 0.5rem;">
        POPULAR CITIES
    </p>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    cities = ['Mumbai', 'Delhi', 'Bangalore',
              'Chennai', 'Hyderabad', 'Kolkata']
    for i, city in enumerate(cities):
        with cols[i % 3]:
            if st.button(city, key=f"btn_{city}",
                         use_container_width=True):
                st.session_state.city = city
                st.rerun()

    # powered by
    st.markdown("""
    <div style="text-align:center; margin-top:2rem;">
        <p style="color:rgba(255,255,255,0.3); font-size:11px; 
                  letter-spacing:0.08em; margin-bottom:8px;">
            POWERED BY
        </p>
        <span style="background:rgba(100,200,150,0.2); color:#6DC89A;
                     border-radius:20px; padding:4px 10px; 
                     font-size:11px; margin:3px;">LSTM</span>
        <span style="background:rgba(100,150,255,0.2); color:#6B9FFF;
                     border-radius:20px; padding:4px 10px;
                     font-size:11px; margin:3px;">LightGBM</span>
        <span style="background:rgba(255,180,100,0.2); color:#FFB464;
                     border-radius:20px; padding:4px 10px;
                     font-size:11px; margin:3px;">XGBoost</span>
        <span style="background:rgba(200,100,255,0.2); color:#C87AFF;
                     border-radius:20px; padding:4px 10px;
                     font-size:11px; margin:3px;">Random Forest</span>
        <span style="background:rgba(255,100,100,0.2); color:#FF8080;
                     border-radius:20px; padding:4px 10px;
                     font-size:11px; margin:3px;">VAR</span>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# FORECAST PAGE
# ═══════════════════════════════════════════════════════
else:

    # ─── FETCH FORECAST ────────────────────────────────
    if st.session_state.forecast is None:
        with st.spinner(f"Fetching forecast for {st.session_state.city}..."):
            try:
                coords = st.session_state.coordinates
                if coords:
                    st.session_state.forecast = forecast_city(
                        st.session_state.city,
                        days = 8,
                        lat  = coords['lat'],
                        lon  = coords['lon'],
                        alt  = coords['alt']
                    )
                else:
                    st.session_state.forecast = forecast_city(
                        st.session_state.city, days=8
                    )
            except Exception as e:
                st.error(f"Could not forecast {st.session_state.city}: {e}")
                st.session_state.city        = None
                st.session_state.forecast    = None
                st.session_state.coordinates = None
                st.rerun()

    forecast  = st.session_state.forecast
    city_name = st.session_state.city

    # ─── GET ZONE INFO ─────────────────────────────────
    city_info = get_city_info(city_name)
    if city_info:
        zone = city_info['zone']
    elif st.session_state.coordinates:
        # use already stored coordinates — no extra API call
        coords = st.session_state.coordinates
        zone = get_zone_from_coordinates(
            coords['lat'], coords['lon']
        )
        if zone is None:
            zone = "india"
    else:
        zone = "india"

    zone_display = zone.replace('zone1_', '').replace('zone2_', '') \
                       .replace('zone3_', '').replace('zone4_', '') \
                       .replace('zone5_', '').replace('zone6_', '') \
                       .replace('_', ' ').title()

    # ─── TODAY'S VALUES ────────────────────────────────
    today    = forecast.iloc[0]
    temp     = round(float(today['temperature']),   1)
    precip   = round(float(today['precipitation']), 1)
    wind     = round(float(today['windspeed']),     1)
    humidity = round(float(today['humidity']),      1)

    # ─── DERIVED VALUES ────────────────────────────────
    feels_like = round(temp + (humidity - 40) * 0.1, 1)

    if precip > 10:
        condition, cond_dot = "Heavy Rain",  "#4FC3F7"
    elif precip > 2:
        condition, cond_dot = "Light Rain",  "#29B6F6"
    elif humidity > 85:
        condition, cond_dot = "Cloudy",      "#90A4AE"
    elif temp > 35:
        condition, cond_dot = "Hot & Sunny", "#FFA726"
    else:
        condition, cond_dot = "Clear",       "#66BB6A"

    if wind < 10:
        wind_desc = "Calm"
    elif wind < 25:
        wind_desc = "Light breeze"
    elif wind < 50:
        wind_desc = "Strong wind"
    else:
        wind_desc = "Storm ⚠️"

    if precip > 15:
        rain_prob = 95
    elif precip > 10:
        rain_prob = 85
    elif precip > 5:
        rain_prob = 70
    elif precip > 2:
        rain_prob = 55
    elif precip > 0.5:
        rain_prob = 35
    elif precip > 0:
        rain_prob = 15
    else:
        rain_prob = 5

    if precip > 10:
        suggestion = "Carry your umbrella — heavy rain expected today."
    elif precip > 2:
        suggestion = "Light rain likely — keep an umbrella handy."
    elif temp > 35:
        suggestion = "Very hot today — stay hydrated and avoid noon sun."
    elif humidity > 85:
        suggestion = "High humidity — feels muggy outside."
    elif wind > 25:
        suggestion = "Strong winds today — secure loose items."
    else:
        suggestion = "Pleasant weather — great day to go outside."

    # ─── BACK BUTTON ───────────────────────────────────
    if st.button("← Back"):
        st.session_state.city        = None
        st.session_state.forecast    = None
        st.session_state.coordinates = None
        st.rerun()

    # ─── MAIN WEATHER CARD ─────────────────────────────

    weather_card_html = f"""
    <div style="background:linear-gradient(160deg,{bg_color},#0A1428);
                border-radius:24px; padding:1.5rem;
                margin-bottom:1rem; color:white; font-family:sans-serif;">

        <p style="color:rgba(255,255,255,0.6); font-size:13px; margin:0 0 8px;">
            {greeting}, {city_name}
        </p>

        <div style="display:flex; justify-content:space-between;
                    align-items:flex-start;">
            <div>
                <h1 style="font-size:28px; font-weight:600;
                           margin:0 0 4px; color:white;">{city_name}</h1>
                <div>
                    <span style="color:rgba(255,255,255,0.5);
                                 font-size:13px;">India</span>
                    &nbsp;
                    <span style="background:rgba(100,150,255,0.25);
                                 border-radius:20px; padding:2px 10px;
                                 font-size:12px; color:#A8C4FF;">
                        {zone_display}
                    </span>
                </div>
                <p style="font-size:72px; font-weight:300;
                          margin:0.5rem 0 0; line-height:1;
                          color:white;">{temp}°</p>
            </div>

            <div style="text-align:right; padding-top:4px;">
                <p style="font-size:12px; color:rgba(255,255,255,0.5);
                          margin:0 0 4px;">{current_time}</p>
                <p style="font-size:18px; font-weight:500;
                          color:white; margin:0 0 6px;">{condition}</p>
                <p style="font-size:13px; color:rgba(255,255,255,0.6);
                          margin:0 0 4px;">Feels like {feels_like}°C</p>
                <p style="font-size:12px; color:rgba(255,255,255,0.4);
                          margin:0;">{wind_desc}</p>
            </div>
        </div>

        <div style="margin-top:1rem; display:flex; flex-wrap:wrap;">
            <span style="background:rgba(255,255,255,0.1);
                         border-radius:20px; padding:5px 12px;
                         font-size:13px; color:white;
                         margin-right:6px; margin-bottom:6px;">
                💨 {wind} km/h
            </span>
            <span style="background:rgba(255,255,255,0.1);
                         border-radius:20px; padding:5px 12px;
                         font-size:13px; color:white;
                         margin-right:6px; margin-bottom:6px;">
                💧 {humidity}% humidity
            </span>
            <span style="background:rgba(255,255,255,0.1);
                         border-radius:20px; padding:5px 12px;
                         font-size:13px; color:white;
                         margin-bottom:6px;">
                🌧️ {rain_prob}% rain
            </span>
        </div>
    </div>
    """
    components.html(weather_card_html, height=280)

    # ─── 7 DAY FORECAST STRIP ──────────────────────────
    days_html = ""
    for i, row in forecast.iloc[1:].iterrows():
        day_name  = (datetime.now() + timedelta(days=i)).strftime('%a')
        day_temp  = round(float(row['temperature']), 1)
        day_prec  = max(0.0, round(float(row['precipitation']), 1))

        if day_prec > 10:
            day_rain, icon = 95, "🌧️"
        elif day_prec > 5:
            day_rain, icon = 70, "🌧️"
        elif day_prec > 2:
            day_rain, icon = 55, "🌦️"
        elif day_prec > 0.5:
            day_rain, icon = 35, "🌦️"
        elif float(row['humidity']) > 85:
            day_rain, icon = 15, "☁️"
        elif float(row['temperature']) > 35:
            day_rain, icon = 5,  "☀️"
        else:
            day_rain, icon = 5,  "🌤️"

        highlight = "background:rgba(100,150,255,0.25);" \
                    "border:1px solid rgba(100,150,255,0.4);" \
                    if i == 1 else "background:rgba(255,255,255,0.07);"

        days_html += f"""
        <div style="{highlight} border-radius:14px;
                    padding:10px 6px; text-align:center;
                    flex:1; min-width:0;">
            <p style="font-size:11px; color:rgba(255,255,255,0.6);
                      margin:0 0 6px; font-weight:500;">{day_name}</p>
            <p style="font-size:20px; margin:0 0 4px;">{icon}</p>
            <p style="font-size:15px; font-weight:500;
                      color:white; margin:0;">{day_temp}°</p>
            <p style="font-size:10px; color:#4FC3F7;
                      margin:4px 0 0;">{day_rain}% rain</p>
        </div>
        """

    components.html(f"""
    <div style="margin-bottom:1rem; font-family:sans-serif;">
        <p style="color:rgba(255,255,255,0.4); font-size:11px;
                  letter-spacing:0.08em; margin:0 0 0.75rem;">
            7-DAY FORECAST
        </p>
        <div style="display:flex; gap:6px;">
            {days_html}
        </div>
    </div>
    """, height=140)

    # ─── MODEL INFO CARD ───────────────────────────────
    from database import get_zone_models
    zone_models_df = get_zone_models(zone)

    if zone_models_df is not None and len(zone_models_df) > 0:
        model_rows = ""
        for _, row in zone_models_df.iterrows():
            if row['model_type'] == 'LSTM':
                color = "#6DC89A"
            elif row['model_type'] == 'LightGBM':
                color = "#6B9FFF"
            elif row['model_type'] == 'RF':
                color = "#FFB464"
            else:
                color = "#C87AFF"

            model_rows += f"""
            <div style="display:flex; justify-content:space-between;
                        align-items:center; margin-bottom:8px;">
                <span style="color:rgba(255,255,255,0.6); font-size:13px;">
                    {row['variable'].title()}
                </span>
                <div>
                    <span style="color:{color}; font-size:13px;
                                 font-weight:500; margin-right:8px;">
                        {row['model_type']}
                    </span>
                    <span style="color:rgba(255,255,255,0.35); font-size:11px;">
                        RMSE {round(row['rmse'], 2)}
                    </span>
                </div>
            </div>
            """

        components.html(f"""
        <div style="font-family:sans-serif;
                    background:rgba(30,40,80,0.9);
                    border-radius:16px; padding:1rem 1.25rem;
                    border:1px solid rgba(100,120,200,0.2);
                    margin-bottom:10px;">
            <p style="color:rgba(255,255,255,0.35); font-size:11px;
                      letter-spacing:0.08em; margin:0 0 0.75rem;">
                ACTIVE MODELS — {zone_display.upper()}
            </p>
            {model_rows}
        </div>
        """, height=180)

    # ─── SMART SUGGESTION ──────────────────────────────
    components.html(f"""
    <div style="font-family:sans-serif;
                background:rgba(255,255,255,0.06);
                border-radius:12px; padding:14px 16px;
                margin-bottom:10px; text-align:center;">
        <p style="color:rgba(255,255,255,0.8); font-size:14px;
                  margin:0; font-style:italic;">
            💡 {suggestion}
        </p>
    </div>
    """, height=70)

    # ─── RAIN ANIMATION ────────────────────────────────
    if condition in ['Light Rain', 'Heavy Rain']:
        components.html("""
        <style>
        .rain-wrap { position:fixed; top:0; left:0;
                     width:100vw; height:100vh;
                     pointer-events:none; z-index:9999;
                     overflow:hidden; }
        .drop { position:absolute; width:1px;
                background:linear-gradient(transparent,#4FC3F7);
                animation:fall linear infinite; opacity:0.5; }
        @keyframes fall {
            0%  { transform:translateY(-100px); }
            100%{ transform:translateY(110vh); }
        }
        </style>
        <div class="rain-wrap" id="rain"></div>
        <script>
        const r = document.getElementById('rain');
        for(let i=0;i<60;i++){
            const d = document.createElement('div');
            d.className = 'drop';
            d.style.left = Math.random()*100+'%';
            d.style.height = (Math.random()*50+30)+'px';
            d.style.animationDuration = (Math.random()*0.6+0.3)+'s';
            d.style.animationDelay = (Math.random()*2)+'s';
            r.appendChild(d);
        }
        </script>
        """, height=0)

    # ─── CHART TABS ────────────────────────────────────
    days_labels = [
        (datetime.now() + timedelta(days=i+1)).strftime('%a')
        for i in range(7)
    ]

    def make_bar_chart(values, color):
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x = days_labels,
            y = values,
            marker_color      = color,
            marker_line_width = 0,
            showlegend        = False
        ))
        fig.update_layout(
            paper_bgcolor = 'rgba(0,0,0,0)',
            plot_bgcolor  = 'rgba(0,0,0,0)',
            font_color    = 'white',
            height        = 180,
            margin        = dict(l=20, r=20, t=10, b=20),
            xaxis         = dict(showgrid=False, fixedrange=True),
            yaxis         = dict(showgrid=False, visible=False, fixedrange=True),
            bargap        = 0.15,
            showlegend    = False,
            dragmode      = False
        )
        return fig

    tab1, tab2, tab3, tab4 = st.tabs(
        ["🌡️ Temp", "🌧️ Rain", "💨 Wind", "💧 Humidity"]
    )

    with tab1:
        values = [round(float(v), 1)
                  for v in forecast['temperature'].iloc[1:]]
        st.plotly_chart(
            make_bar_chart(values, 'rgba(100,150,255,0.8)'),
            use_container_width=True,
            config={
                'displayModeBar': False,
                'scrollZoom':     False,
                'staticPlot':     True    
            }
        )

    with tab2:
        values = [max(0.1, round(float(v), 1))
                  for v in forecast['precipitation'].iloc[1:]]
        st.plotly_chart(
            make_bar_chart(values, 'rgba(100,200,150,0.8)'),
            use_container_width=True,
            config={
                'displayModeBar': False,
                'scrollZoom':     False,
                'staticPlot':     True    
            }
        )

    with tab3:
        values = [round(float(v), 1)
                  for v in forecast['windspeed'].iloc[1:]]
        st.plotly_chart(
            make_bar_chart(values, 'rgba(200,100,255,0.8)'),
            use_container_width=True,
            config={
                'displayModeBar': False,
                'scrollZoom':     False,
                'staticPlot':     True    
            }
        )

    with tab4:
        values = [round(float(v), 1)
                  for v in forecast['humidity'].iloc[1:]]
        st.plotly_chart(
            make_bar_chart(values, 'rgba(100,220,255,0.8)'),
            use_container_width=True,
            config={
                'displayModeBar': False,
                'scrollZoom':     False,
                'staticPlot':     True    
            }
        )
