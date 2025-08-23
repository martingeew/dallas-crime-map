# Dallas Crime Map 2024

[![Live Demo](https://img.shields.io/badge/Live%20Demo-View%20Map-blue?style=for-the-badge)](https://martingeew.github.io/dallas-crime-map/reports/dallas_property_crimes_2024_map.html)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Site-green?style=for-the-badge)](https://martingeew.github.io/dallas-crime-map/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://python.org)
[![Folium](https://img.shields.io/badge/Folium-Interactive%20Maps-red?style=for-the-badge)](https://python-visualization.github.io/folium/)

An interactive web-based visualization of Dallas Police Department incident data, focusing on property crimes and burglary incidents for 2024. This project creates geographic visualizations using Python, Folium, and the Nominatim geocoding API to help analyze crime patterns across different zip codes in Dallas.

## 🚀 Live Demo

**[📍 View Interactive Crime Map](https://martingeew.github.io/dallas-crime-map/reports/dallas_property_crimes_2024_map.html)**

**[🌐 Project Home Page](https://martingeew.github.io/dallas-crime-map/)**

## 📋 Table of Contents

- [Features](#-features)
- [Technologies Used](#-technologies-used)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Data Sources](#-data-sources)
- [How It Works](#-how-it-works)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

- **🗺️ Interactive Map Visualization**: Clickable markers with detailed popup information
- **📊 Data-Driven Insights**: Circle sizes represent incident counts for visual impact
- **🎨 Color-Coded Crime Types**: Distinct colors for different types of property crimes
- **📍 Zip Code Aggregation**: Geographic analysis by Dallas zip codes
- **🔍 Property Crime Focus**: Specialized filtering for burglary, theft, and property-related incidents
- **⚡ Smart Geocoding Cache**: Efficient coordinate caching to minimize API calls
- **📱 Responsive Design**: Works on desktop and mobile devices
- **🎛️ Layer Controls**: Toggle different crime types on/off for focused analysis

## 🛠️ Technologies Used

- **Python 3.8+**: Core programming language
- **Folium**: Interactive map generation
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Requests**: HTTP requests for geocoding
- **Nominatim API**: OpenStreetMap geocoding service
- **GitHub Pages**: Static site hosting

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Git (optional, for cloning)

### Step-by-Step Setup

1. **Clone the repository** (or download as ZIP):
   ```bash
   git clone https://github.com/martingeew/dallas-crime-map.git
   cd dallas-crime-map
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate
   
   # macOS/Linux
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**:
   ```bash
   python -c "import folium, pandas, numpy, requests; print('All dependencies installed successfully!')"
   ```

### Required Dependencies

The project uses the following Python packages:

```txt
folium==0.20.0
pandas==2.3.1
numpy==2.3.2
requests==2.32.4
branca==0.8.1
```

## 🚀 Usage

### Generate the Crime Map

Run the main visualization script:

```bash
python src/visualization/visualize_police_incidents_map.py
```

### What Happens When You Run It

1. **Data Loading**: Loads Dallas PD incident data from CSV file
2. **Data Filtering**: Filters for property crimes and 2024 incidents
3. **Geocoding**: Converts zip codes to coordinates (cached for efficiency)
4. **Map Generation**: Creates interactive Folium map with markers
5. **Output**: Saves HTML map to `reports/dallas_property_crimes_2024_map.html`

### Expected Output

```
Successfully loaded 1,234 police incident records
Filtering for property crime incidents...
Found 567 property crime incidents for 2024
Loading coordinate cache...
Found cached coordinates for 45 zip codes
Geocoding 3 new zip codes...
Geocoding 75201: (32.7812, -96.7969)
Creating incident map...
Map saved to: reports/dallas_property_crimes_2024_map.html
```

### Opening the Map

After generation, open the HTML file in any web browser:

- **Local file**: Open `reports/dallas_property_crimes_2024_map.html`
- **Live version**: [View online](https://martingeew.github.io/dallas-crime-map/reports/dallas_property_crimes_2024_map.html)

## 📁 Project Structure

```
dallas_crime_map/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── index.html                         # GitHub Pages home page
├── CLAUDE.md                          # Development instructions
├── data/
│   └── external/
│       ├── Public_Safety_-_Police_Incidents_20250729.csv  # Source data
│       └── dallas_zip_coordinates.json                    # Geocoding cache
├── src/
│   └── visualization/
│       ├── __init__.py
│       └── visualize_police_incidents_map.py              # Main script
└── reports/
    └── dallas_property_crimes_2024_map.html               # Generated map
```

### Key Files Explained

- **`src/visualization/visualize_police_incidents_map.py`**: Main application script containing all map generation logic
- **`data/external/Public_Safety_-_Police_Incidents_20250729.csv`**: Dallas Police Department incident data
- **`data/external/dallas_zip_coordinates.json`**: Cached zip code coordinates to avoid repeated API calls
- **`reports/dallas_property_crimes_2024_map.html`**: Generated interactive map output

## 📊 Data Sources

### Primary Dataset

**Source**: Dallas Police Department - Public Safety Incidents  
**Format**: CSV file with the following key columns:

| Column | Description | Example |
|--------|-------------|---------|
| `count` | Number of incidents | 5 |
| `Year of Incident` | Year when incident occurred | 2024 |
| `Type of Incident` | Description of crime type | "BURGLARY OF RESIDENCE" |
| `Division` | Police division | "NORTHEAST" |
| `Zip Code` | Location zip code | "75201" |

### Property Crime Types Included

The visualization focuses on property crimes identified by these keywords:

- **BURGLARY** (residential, business, vehicle)
- **THEFT** (various types)
- **ROBBERY** (aggravated, simple)
- **LARCENY**
- **STOLEN VEHICLE**
- **FRAUD**
- **FORGERY**

### Geocoding

- **Service**: Nominatim API (OpenStreetMap)
- **Rate Limiting**: 0.1 second delay between requests
- **Caching**: Coordinates saved locally to avoid repeated API calls
- **Accuracy**: Zip code level precision

## ⚙️ How It Works

### Data Processing Pipeline

1. **Data Loading**: 
   ```python
   def load_police_data():
       # Loads CSV data with error handling
   ```

2. **Crime Filtering**:
   ```python
   def filter_for_burglary_property_incidents(df):
       # Filters for property crimes using keyword matching
   ```

3. **Geocoding System**:
   ```python
   def create_zip_coordinates_cache(zip_codes):
       # Converts zip codes to lat/lon coordinates
   ```

4. **Map Generation**:
   ```python
   def create_incident_map(map_data, coordinates):
       # Creates Folium map with markers and popups
   ```

### Visualization Features

- **Circle Markers**: Size proportional to incident count
- **Color Coding**: HSV color space for distinct crime type colors
- **Interactive Popups**: Show zip code, total crimes, and breakdown
- **Layer Controls**: Toggle different incident types
- **Custom Legend**: Embedded HTML explaining map features

### Performance Optimizations

- **Coordinate Caching**: Prevents repeated geocoding API calls
- **Rate Limiting**: Respects Nominatim API usage policies
- **Data Filtering**: Focuses on specific crime types and year
- **Efficient Aggregation**: Groups incidents by zip code

## 🤝 Contributing

We welcome contributions to improve the Dallas Crime Map project! Here's how you can help:

### Ways to Contribute

- **🐛 Bug Reports**: Found an issue? [Open an issue](https://github.com/martingeew/dallas-crime-map/issues)
- **💡 Feature Requests**: Have an idea? [Suggest a feature](https://github.com/martingeew/dallas-crime-map/issues)
- **📝 Documentation**: Improve README, comments, or docstrings
- **🔧 Code Improvements**: Optimize performance, add features, fix bugs

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style

- Follow PEP 8 Python style guidelines
- Add docstrings to all functions
- Include type hints where appropriate
- Write meaningful commit messages

### Testing

Before submitting changes:

```bash
# Test the main functionality
python src/visualization/visualize_police_incidents_map.py

# Verify all dependencies work
python -c "import folium, pandas, numpy, requests; print('Dependencies OK')"
```

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Dallas Police Department** for providing public incident data
- **OpenStreetMap** and **Nominatim** for geocoding services
- **Folium** community for excellent mapping tools
- **Pandas** and **NumPy** teams for data processing capabilities

## 📞 Contact

- **Repository**: [github.com/martingeew/dallas-crime-map](https://github.com/martingeew/dallas-crime-map)
- **Live Demo**: [martingeew.github.io/dallas-crime-map](https://martingeew.github.io/dallas-crime-map/)
- **Issues**: [GitHub Issues](https://github.com/martingeew/dallas-crime-map/issues)

---
