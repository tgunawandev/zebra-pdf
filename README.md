# PDF to Zebra Printer

Simple Python application that prints PDF files to Zebra printers connected via USB. Provides both CLI and REST API interfaces.

## Features

- **CLI Interface**: Command-line tool for printing PDFs
- **REST API**: HTTP API for web applications
- **USB Connection**: Works with USB-connected Zebra printers via CUPS
- **Error Handling**: Comprehensive error handling and validation
- **File Upload**: Support for PDF file uploads via API

## Prerequisites

1. **Zebra Printer**: Connected via USB and configured in CUPS
2. **Python 3.7+**: Required for running the application
3. **CUPS**: Linux printing system (usually pre-installed)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure your Zebra printer is connected and visible in CUPS:
```bash
lpstat -p
```

## Usage

### CLI Interface

**Print a PDF file:**
```bash
python pdf_printer.py print /path/to/your/file.pdf
```

**Print multiple copies:**
```bash
python pdf_printer.py print /path/to/your/file.pdf --copies 3
```

**Check printer status:**
```bash
python pdf_printer.py status
```

**Example with your sample PDF:**
```bash
python pdf_printer.py print "/home/tgunawan/Downloads/QR Labels - W-CPN_OUT_00002.pdf"
```

### REST API

**Start the API server:**
```bash
python api_server.py --host 0.0.0.0 --port 5000
```

**API Endpoints:**

1. **Health Check**
   ```bash
   curl http://localhost:5000/api/health
   ```

2. **Printer Status**
   ```bash
   curl http://localhost:5000/api/status
   ```

3. **Upload and Print PDF**
   ```bash
   curl -X POST -F "file=@/path/to/file.pdf" -F "copies=1" \
        http://localhost:5000/api/print
   ```

4. **Print Existing File on Server**
   ```bash
   curl -X POST -H "Content-Type: application/json" \
        -d '{"file_path":"/path/to/file.pdf","copies":1}' \
        http://localhost:5000/api/print-file
   ```

### Example API Usage with curl

```bash
# Upload and print your sample PDF
curl -X POST -F "file=@/home/tgunawan/Downloads/QR Labels - W-CPN_OUT_00002.pdf" \
     http://localhost:5000/api/print

# Print existing file on server
curl -X POST -H "Content-Type: application/json" \
     -d '{"file_path":"/home/tgunawan/Downloads/QR Labels - W-CPN_OUT_00002.pdf","copies":1}' \
     http://localhost:5000/api/print-file
```

## API Response Format

All API responses follow this format:

**Success Response:**
```json
{
  "success": true,
  "message": "PDF printed successfully (1 copies)",
  "filename": "example.pdf",
  "copies": 1
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "No Zebra printer found in CUPS"
}
```

## Troubleshooting

**No printer found:**
- Check if printer is connected: `lsusb`
- Check CUPS printers: `lpstat -p`
- Add printer to CUPS if not visible

**Permission errors:**
- Make sure user is in `lp` group: `sudo usermod -a -G lp $USER`
- Restart after adding to group

**API server won't start:**
- Check if port is available: `netstat -tulpn | grep :5000`
- Try different port: `python api_server.py --port 5001`

## File Structure

```
zebra-pdf/
├── pdf_printer.py     # CLI interface and core printing logic
├── api_server.py      # REST API server
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Notes

- Maximum file size for API uploads: 16MB
- Supported file format: PDF only
- Copy limit: 1-10 copies per print job
- Uses CUPS for reliable PDF printing to Zebra printers