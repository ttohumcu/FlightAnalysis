from flask import Flask, render_template, request, jsonify
import csv
import io

app = Flask(__name__)

def parse_csv(file_content):
    """Parses the CSV content and extracts key flight data."""
    if not file_content:
        return None

    try:
        content_text = file_content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content_text))
        header = next(csv_reader)
        
        # Find indices of relevant columns
        lat_index = header.index("OSD.latitude")
        lon_index = header.index("OSD.longitude")
        alt_index = header.index("OSD.altitude")
        speed_index = header.index("OSD.xSpeed")
        battery_index = header.index("BATTERY.chargeLevel")
        fly_time_index = header.index("OSD.flyTime")

        telemetry_data = []
        for row in csv_reader:
            telemetry_data.append({
                "lat": float(row[lat_index]),
                "lon": float(row[lon_index]),
                "altitude": float(row[alt_index]),
                "speed": float(row[speed_index]),
                "battery": int(row[battery_index]),
                "flyTime": float(row[fly_time_index])
            })
        
        return telemetry_data

    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return None

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handles file uploads and returns flight data."""
    if 'files[]' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    files = request.files.getlist('files[]')
    
    flight_data = {}

    for file in files:
        filename = file.filename
        content = file.read()
        
        if filename.endswith('.csv'):
            flight_data['telemetry'] = parse_csv(content)
        elif filename.endswith('.kml'):
            flight_data['kml'] = content.decode('utf-8')
        elif filename.endswith('.geojson'):
            flight_data['geojson'] = content.decode('utf-8')
        elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # In a real application, you would save these files 
            # and return URLs to them. For this example, we'll
            # just acknowledge that they were received.
            if 'images' not in flight_data:
                flight_data['images'] = []
            flight_data['images'].append(filename)


    return jsonify(flight_data)

if __name__ == '__main__':
    app.run(debug=True)
