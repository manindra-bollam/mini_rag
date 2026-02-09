"""
Generate sample PDF files for testing the RAG system.

This script creates 5 sample PDF files about sensors.
"""
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except ImportError:
    print("Error: reportlab not installed")
    print("Install with: pip install reportlab")
    exit(1)


def create_sample_pdfs() -> None:
    """Create sample PDF files."""
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    # Sample content for 5 PDFs
    documents = {
        "temperature_sensors": [
            "Temperature Sensors Overview",
            "This document covers various temperature sensors used in industrial applications.",
            "",
            "Type K Thermocouples:",
            "- Operating range: -200°C to 1200°C",
            "- Accuracy: ±2.2°C or ±0.75%",
            "- Applications: General purpose industrial measurements",
            "",
            "Type N Thermocouples:",
            "- Operating range: -270°C to 1300°C",
            "- Accuracy: ±2.2°C or ±0.75%",
            "- Better oxidation resistance than Type K",
            "",
            "RTD Sensors (PT100):",
            "- Operating range: -200°C to 850°C",
            "- Accuracy: ±0.15°C to ±0.35°C",
            "- High accuracy and stability",
            "- Common in pharmaceutical and food industries",
        ],
        "pressure_sensors": [
            "Pressure Measurement Technologies",
            "Overview of pressure sensors and their applications.",
            "",
            "Strain Gauge Pressure Sensors:",
            "- Pressure range: 0 to 10,000 psi",
            "- Accuracy: ±0.25% of full scale",
            "- Used in hydraulic systems",
            "",
            "Capacitive Pressure Sensors:",
            "- Pressure range: 0.1 to 100 bar",
            "- High accuracy and low drift",
            "- Suitable for clean gases and liquids",
            "",
            "Piezoelectric Pressure Sensors:",
            "- Fast response time (<1 microsecond)",
            "- Dynamic pressure measurements",
            "- Common in combustion analysis",
        ],
        "flow_sensors": [
            "Flow Measurement Devices",
            "Guide to selecting and using flow sensors.",
            "",
            "Turbine Flow Meters:",
            "- Flow range: 0.1 to 10,000 GPM",
            "- Accuracy: ±0.5% of reading",
            "- Clean liquid applications",
            "",
            "Magnetic Flow Meters:",
            "- Suitable for conductive liquids",
            "- No moving parts",
            "- Accuracy: ±0.2% to ±0.5%",
            "- Works with dirty or corrosive fluids",
            "",
            "Ultrasonic Flow Meters:",
            "- Non-invasive installation",
            "- No pressure drop",
            "- Transit-time and Doppler types available",
        ],
        "humidity_sensors": [
            "Humidity Sensing Technology",
            "Comprehensive guide to humidity measurement.",
            "",
            "Capacitive Humidity Sensors:",
            "- Humidity range: 0 to 100% RH",
            "- Accuracy: ±2% RH",
            "- Temperature range: -40°C to 125°C",
            "- Fast response time",
            "",
            "Resistive Humidity Sensors:",
            "- Lower cost option",
            "- Accuracy: ±3% to ±5% RH",
            "- Suitable for basic applications",
            "",
            "Thermal Conductivity Sensors:",
            "- Used in harsh environments",
            "- Can operate at high temperatures up to 400°C",
            "- Less common but very robust",
        ],
        "level_sensors": [
            "Level Measurement Solutions",
            "Technologies for liquid and solid level measurement.",
            "",
            "Ultrasonic Level Sensors:",
            "- Non-contact measurement",
            "- Range: Up to 20 meters",
            "- Accuracy: ±0.25% of measured distance",
            "- Suitable for tanks and silos",
            "",
            "Radar Level Sensors:",
            "- Immune to temperature and pressure changes",
            "- Can measure through foam and vapor",
            "- Operating temperature: -60°C to 400°C",
            "- High accuracy in demanding conditions",
            "",
            "Float Level Sensors:",
            "- Simple mechanical design",
            "- Cost-effective solution",
            "- Direct measurement",
            "- Limited to relatively clean liquids",
        ],
    }
    
    print("Creating sample PDF files...")
    
    for doc_name, content_lines in documents.items():
        pdf_path = data_dir / f"{doc_name}.pdf"
        
        # Create PDF
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        width, height = letter
        
        # Add content
        y_position = height - 50
        for line in content_lines:
            if y_position < 50:  # New page if needed
                c.showPage()
                y_position = height - 50
            
            c.drawString(50, y_position, line)
            y_position -= 20
        
        c.save()
        print(f"Created: {pdf_path}")
    
    print(f"\nSuccessfully created {len(documents)} PDF files in {data_dir}/")


if __name__ == "__main__":
    create_sample_pdfs()