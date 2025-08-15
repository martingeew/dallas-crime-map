import pandas as pd
import numpy as np
from pathlib import Path
import folium
from folium import plugins
import requests
import json
import time
from collections import Counter
import colorsys


def load_police_data():
    """Load the Dallas police incidents data."""
    data_path = (
        Path(__file__).parent.parent.parent
        / "data"
        / "external"
        / "Public_Safety_-_Police_Incidents_20250729.csv"
    )

    try:
        df = pd.read_csv(data_path)
        print(f"Successfully loaded {len(df)} police incident records")
        return df
    except FileNotFoundError:
        print(f"Error: Could not find file at {data_path}")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def geocode_zip_code(zip_code, delay=0.1):
    """
    Geocode a zip code using Nominatim API.
    Returns (lat, lon) tuple or None if not found.
    """
    try:
        # Add delay to respect API rate limits
        time.sleep(delay)

        url = f"https://nominatim.openstreetmap.org/search"
        params = {
            "q": f"{zip_code}, Dallas, Texas, USA",
            "format": "json",
            "limit": 1,
            "countrycodes": "us",
        }
        headers = {"User-Agent": "Dallas-Police-Incidents-Mapping/1.0"}

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return (lat, lon)
        else:
            print(f"No coordinates found for zip code {zip_code}")
            return None

    except Exception as e:
        print(f"Error geocoding zip code {zip_code}: {e}")
        return None


def create_zip_coordinates_cache(df):
    """
    Create a cache of zip code coordinates.
    This will take some time due to API rate limiting.
    """
    print("Creating zip code coordinates cache...")

    # Get unique zip codes (excluding NaN)
    unique_zips = df[df["Zip Code"].notna()]["Zip Code"].unique()

    coordinates = {}
    total_zips = len(unique_zips)

    print(f"Geocoding {total_zips} unique zip codes (this may take several minutes)...")

    for i, zip_code in enumerate(unique_zips, 1):
        print(f"Geocoding {i}/{total_zips}: {int(zip_code)}")

        coords = geocode_zip_code(int(zip_code))
        if coords:
            coordinates[int(zip_code)] = coords

        # Progress update every 10 zip codes
        if i % 10 == 0:
            print(f"Progress: {i}/{total_zips} completed")

    print(f"Successfully geocoded {len(coordinates)}/{total_zips} zip codes")
    return coordinates


def generate_colors_for_incident_types(incident_types, max_colors=50):
    """
    Generate distinct colors for incident types.
    Uses HSV color space to create visually distinct colors.
    """
    colors = {}
    n_types = min(len(incident_types), max_colors)

    # Generate colors using golden ratio for better distribution
    golden_ratio = 0.618033988749895

    for i, incident_type in enumerate(incident_types[:max_colors]):
        hue = (i * golden_ratio) % 1.0
        # Use high saturation and medium-high value for vibrant colors
        saturation = 0.7 + (i % 3) * 0.1  # 0.7, 0.8, 0.9
        value = 0.8 + (i % 2) * 0.1  # 0.8, 0.9

        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        hex_color = "#%02x%02x%02x" % tuple(int(c * 255) for c in rgb)
        colors[incident_type] = hex_color

    # Use gray for any remaining incident types
    for incident_type in incident_types[max_colors:]:
        colors[incident_type] = "#808080"

    return colors


def filter_for_burglary_property_incidents(df):
    """
    Filter data for burglary and property-related incidents only.
    Groups all into a single 'Property Crime' category.
    """
    # Define keywords for burglary and property-related crimes (excluding TRESPASS, FRAUD, FORGERY)
    property_keywords = [
        "BURGLARY",
        "THEFT",
        "ROBBERY",
        "STOLEN",
        "BREAKING",
        "ENTERING",
        "LARCENY",
        "EMBEZZLEMENT",
        "AUTO THEFT",
        "CRIMINAL MISCHIEF",
        "VANDALISM",
        "SHOPLIFTING",
    ]

    # Create filter mask
    incident_type_col = df["Type of Incident"].astype(str).str.upper()
    mask = incident_type_col.str.contains(
        "|".join(property_keywords), na=False, regex=True
    )

    filtered_df = df[mask].copy()

    # Store original incident types for the description
    filtered_df["Original_Incident_Type"] = filtered_df["Type of Incident"].copy()

    # Group all property crimes into single category
    filtered_df["Type of Incident"] = "Property Crime"

    print(
        f"Filtered to {len(filtered_df)} property/burglary related incidents from {len(df)} total records"
    )

    return filtered_df


def prepare_map_data(df, zip_coordinates):
    """
    Prepare data for mapping by aggregating incidents by zip code and type.
    Filters for 2024 data and burglary/property incidents only.
    """
    print("Preparing map data...")

    # Filter for 2024 data only
    df_2024 = df[df["Year of Incident"] == 2024].copy()
    print(f"Filtered to {len(df_2024)} records from 2024")

    # Filter for burglary and property-related incidents
    df_filtered = filter_for_burglary_property_incidents(df_2024)

    # Filter data with valid zip codes and coordinates
    df_clean = df_filtered[df_filtered["Zip Code"].notna()].copy()
    df_clean = df_clean[df_clean["Zip Code"].isin(zip_coordinates.keys())]

    print(f"After filtering: {len(df_clean)} records with valid zip codes")

    count_column = df_clean.columns[0]  # 'count' column

    # Group by zip code and collect incident details with counts
    incident_details = (
        df_clean.groupby(["Zip Code", "Original_Incident_Type"])[count_column]
        .sum()
        .reset_index()
    )
    incident_counts = (
        incident_details.groupby("Zip Code")
        .apply(lambda x: dict(zip(x["Original_Incident_Type"], x[count_column])))
        .to_dict()
    )

    # Group by zip code for main data
    grouped = (
        df_clean.groupby(["Zip Code", "Type of Incident"])[count_column]
        .sum()
        .reset_index()
    )

    # Add incident counts details
    grouped["Incident_Counts"] = grouped["Zip Code"].map(incident_counts)

    # Add coordinates
    grouped["lat"] = grouped["Zip Code"].map(lambda x: zip_coordinates[x][0])
    grouped["lon"] = grouped["Zip Code"].map(lambda x: zip_coordinates[x][1])

    print(f"Prepared {len(grouped)} zip code/incident type combinations for mapping")
    return grouped


def create_incident_map(map_data, zip_coordinates):
    """
    Create the interactive Folium map.
    """
    print("Creating interactive map...")

    # Center map on Dallas
    dallas_center = [32.7767, -96.7970]

    # Create base map with light theme
    m = folium.Map(location=dallas_center, zoom_start=10, tiles="cartodbpositron")

    # Add alternative light tile layers
    folium.TileLayer("OpenStreetMap").add_to(m)
    folium.TileLayer("Stamen Toner Lite", attr="Stamen").add_to(m)

    # Get incident types and generate colors
    incident_types = map_data["Type of Incident"].unique()
    colors = generate_colors_for_incident_types(incident_types)

    # Calculate marker sizes based on incident counts
    count_column = map_data.columns[2]  # count column
    min_count = map_data[count_column].min()
    max_count = map_data[count_column].max()

    # Scale marker sizes between 5 and 30 pixels
    def scale_marker_size(count):
        if max_count == min_count:
            return 15
        normalized = (count - min_count) / (max_count - min_count)
        return 5 + normalized * 25

    # Create feature groups for each incident type (for layer control)
    feature_groups = {}
    # Limit to top 10 incident types for better performance
    top_incident_types = (
        map_data.groupby("Type of Incident")[count_column].sum().nlargest(10).index
    )
    for incident_type in top_incident_types:
        feature_groups[incident_type] = folium.FeatureGroup(
            name=incident_type[:50]
        )  # Truncate long names

    # Add markers for each incident type/zip combination
    for _, row in map_data.iterrows():
        incident_type = row["Type of Incident"]
        zip_code = int(row["Zip Code"])
        count = row[count_column]
        lat, lon = row["lat"], row["lon"]

        color = colors.get(incident_type, "#808080")
        size = scale_marker_size(count)

        # Get incident counts for this location
        incident_counts_dict = row["Incident_Counts"]

        # Sort incidents by count (descending order)
        sorted_incidents = sorted(
            incident_counts_dict.items(), key=lambda x: x[1], reverse=True
        )

        # Create formatted list with counts
        incident_list = "<br>".join(
            [f"• {incident}: {count:,}" for incident, count in sorted_incidents]
        )

        # Create popup text
        popup_text = f"""
        <b>Zip Code:</b> {zip_code}<br>
        <b>Total Property Crimes:</b> {count:,}<br>
        <br><b>Incident Types (by frequency):</b><br>
        {incident_list}
        """

        # Create marker
        marker = folium.CircleMarker(
            location=[lat, lon],
            radius=size,
            popup=folium.Popup(popup_text, max_width=300),
            color="black",
            weight=1,
            fillColor=color,
            fillOpacity=0.7,
            tooltip=f"Property Crimes: {count:,} incidents",
        )

        # Add to appropriate feature group (if it exists)
        if incident_type in feature_groups:
            marker.add_to(feature_groups[incident_type])
        else:
            marker.add_to(m)

    # Add feature groups to map
    for fg in feature_groups.values():
        fg.add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Add a custom legend
    legend_html = """
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 320px; height: 140px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4>Dallas Property Crimes Map - 2024</h4>
    <p><b>Circle Size:</b> Number of incidents<br>
    <b>Circle Color:</b> Incident type<br>
    <b>Focus:</b> Burglary & Property-related crimes<br>
    <b>Data Source:</b> Dallas Police Department</p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m


def save_coordinates_cache(coordinates, filename="dallas_zip_coordinates.json"):
    """Save zip code coordinates to a JSON file for future use."""
    cache_path = Path(__file__).parent.parent.parent / "data" / "external" / filename

    with open(cache_path, "w") as f:
        json.dump(coordinates, f, indent=2)

    print(f"Saved coordinates cache to {cache_path}")


def load_coordinates_cache(filename="dallas_zip_coordinates.json"):
    """Load zip code coordinates from a JSON file."""
    cache_path = Path(__file__).parent.parent.parent / "data" / "external" / filename

    try:
        with open(cache_path, "r") as f:
            coordinates = json.load(f)

        # Convert string keys back to integers
        coordinates = {int(k): v for k, v in coordinates.items()}
        print(f"Loaded {len(coordinates)} zip code coordinates from cache")
        return coordinates
    except FileNotFoundError:
        print("No coordinates cache found, will need to geocode zip codes")
        return None
    except Exception as e:
        print(f"Error loading coordinates cache: {e}")
        return None


def main():
    """Main function to create the Dallas police incidents map."""
    print("Dallas Police Incidents Interactive Map Generator")
    print("=" * 50)

    # Load police data
    df = load_police_data()
    if df is None:
        return

    # Try to load existing coordinates cache
    zip_coordinates = load_coordinates_cache()

    if zip_coordinates is None:
        # Create new coordinates cache (this will take time)
        print(
            "\nWARNING: Geocoding zip codes will take several minutes due to API rate limits."
        )
        response = input("Continue? (y/n): ")

        if response.lower() != "y":
            print("Operation cancelled.")
            return

        zip_coordinates = create_zip_coordinates_cache(df)

        if zip_coordinates:
            save_coordinates_cache(zip_coordinates)
        else:
            print("Failed to create coordinates cache")
            return

    # Prepare map data
    map_data = prepare_map_data(df, zip_coordinates)

    if len(map_data) == 0:
        print("No mappable data available")
        return

    # Create map
    incident_map = create_incident_map(map_data, zip_coordinates)

    # Save map
    output_path = (
        Path(__file__).parent.parent.parent
        / "reports"
        / "dallas_property_crimes_2024_map.html"
    )
    output_path.parent.mkdir(exist_ok=True)

    incident_map.save(str(output_path))
    print(f"\nInteractive map saved to: {output_path}")
    print("Open the HTML file in a web browser to view the map.")

    # Print summary statistics
    print(f"\nMap Summary:")
    print(f"- Total incident locations: {len(map_data)}")
    print(f"- Unique zip codes: {len(map_data['Zip Code'].unique())}")
    print(f"- Unique incident types: {len(map_data['Type of Incident'].unique())}")
    print(f"- Total incidents mapped: {map_data[map_data.columns[2]].sum():,}")


if __name__ == "__main__":
    # Check if folium is available
    try:
        import folium
    except ImportError:
        print("Error: folium library not found.")
        print("Please install it with: pip install folium")
        exit(1)

    main()
