# External Weather Data

Files in this directory:

- `draw_metadata.csv`: draw date/time/location metadata used for weather matching
- `weather_observations.csv`: cached raw weather observations fetched from KMA API Hub
- `weather_draw_context.csv`: draw-level weather context derived from cached observations

Recommended workflow:

1. run `python main.py weather-fetch` to fill or extend `weather_observations.csv`
2. run `python main.py weather-build` to create `weather_draw_context.csv`
3. use notebooks to analyze the saved files instead of calling the API directly inside notebooks

Environment variable:

```env
KMA_AUTH_KEY=your-issued-key
```

Current usage notes:

- the saved weather context currently supports full draw-level temperature, humidity, wind, pressure, rain-flag, and snow-flag analysis
- rain detection now uses a revised proxy based on the nearest-hour observation and cumulative same-day rainfall when available
- daily aggregate weather fields may still be unavailable depending on API access and saved cache state

Source and attribution:

- source: Korea Meteorological Administration (KMA) API Hub
- API Hub info: https://apihub.kma.go.kr/apiInfo.do
- KMA copyright policy: https://www.kma.go.kr/kma/guide/copyright.jsp

Usage note:

- KMA API Hub states that provided data is subject to applicable KOGL/public-data terms
- KMA copyright guidance indicates KOGL Type 1 public works may be used freely with source attribution
- keep source attribution when redistributing derived CSV outputs from this directory
- do not commit `.env` or any private API key
