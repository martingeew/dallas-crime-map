# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python data visualization project that creates interactive maps of Dallas police incidents, specifically focusing on property crimes and burglary incidents from 2024. The project processes Dallas Police Department incident data and generates Folium-based HTML maps with geographic visualization.

## Development Environment

- **Python Environment**: Uses a virtual environment at `.venv/`
- **Python Executable**: Located at `C:\Users\marti\py_projects\dallas_crime_map\.venv\Scripts\python.exe`

## Required Dependencies

The project requires these Python packages (currently not installed):
```bash
pip install folium pandas numpy requests
```

## Key Commands

### Setup Environment
```bash
# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install folium pandas numpy requests
```

### Run the Application
```bash
# Generate the Dallas crime map
python src/visualization/visualize_police_incidents_map.py
```

### Check Dependencies
```bash
# Verify required packages are installed
python -c "import folium, pandas, numpy, requests; print('All dependencies available')"
```

## Project Structure

### Data Pipeline
1. **Data Input**: Processes `data/external/Public_Safety_-_Police_Incidents_20250729.csv` (Dallas PD incident data)
2. **Geocoding**: Uses Nominatim API to convert zip codes to coordinates
3. **Caching**: Stores geocoded coordinates in `data/external/dallas_zip_coordinates.json` to avoid repeated API calls
4. **Visualization**: Generates interactive Folium map saved to `reports/dallas_property_crimes_2024_map.html`

### Key Files
- `src/visualization/visualize_police_incidents_map.py`: Main application script with complete map generation logic
- `data/external/dallas_zip_coordinates.json`: Cached zip code coordinates (lat/lon pairs)
- `data/external/Public_Safety_-_Police_Incidents_20250729.csv`: Source crime incident data
- `reports/dallas_property_crimes_2024_map.html`: Generated interactive map output

## Application Architecture

### Data Processing Flow
1. **load_police_data()**: Loads CSV data with incident counts, years, types, divisions, and zip codes
2. **filter_for_burglary_property_incidents()**: Filters for property crimes using keyword matching (BURGLARY, THEFT, ROBBERY, etc.)
3. **Geocoding System**: 
   - **load_coordinates_cache()**: Attempts to load existing zip code coordinates
   - **create_zip_coordinates_cache()**: Geocodes zip codes using Nominatim API with rate limiting
   - **save_coordinates_cache()**: Persists coordinates to JSON file
4. **prepare_map_data()**: Aggregates 2024 property crime data by zip code and incident type
5. **create_incident_map()**: Generates Folium map with CircleMarkers, popups, and layer controls

### Visualization Features
- **Interactive Map**: Built with Folium library
- **Marker Sizing**: Circle size represents incident count
- **Color Coding**: Distinct colors for different incident types using HSV color space
- **Popups**: Show zip code, total crimes, and breakdown by incident type
- **Layer Control**: Toggle different incident types on/off
- **Custom Legend**: Embedded HTML legend explaining map features

### Key Design Patterns
- **Caching Strategy**: Geocoding results are cached to avoid repeated API calls and respect rate limits
- **Error Handling**: Comprehensive error handling for file loading, API calls, and data processing
- **Rate Limiting**: Built-in delays for Nominatim API calls to prevent rate limiting
- **Data Filtering**: Focuses specifically on property crimes and 2024 data for targeted analysis

## Data Sources

The application expects Dallas Police Department incident data in CSV format with columns:
- `count`: Number of incidents 
- `Year of Incident`: Year when incident occurred
- `Type of Incident`: Description of crime type
- `Division`: Police division
- `Zip Code`: Location zip code

## Output

The application generates an interactive HTML map at `reports/dallas_property_crimes_2024_map.html` that can be opened in any web browser to explore Dallas property crime patterns by zip code.