# ClipShare

A minimalist online clipboard for sharing text and files with temporary access codes.

## Features

- **Text Sharing**: Share text content with syntax highlighting for various programming languages
- **File Upload**: Upload and share multiple files (images, documents, code files, etc.)
- **Temporary Access**: Content expires automatically (configurable expiration time)
- **Access Codes**: Simple 4-digit numeric codes for easy sharing
- **File Download**: Download individual files or all files as a ZIP archive
- **Image Preview**: Built-in image viewing for common image formats
- **Syntax Highlighting**: Automatic language detection and syntax highlighting for code files
- **Clean UI**: Minimalist, responsive web interface

## Supported File Types

### Programming Languages (with syntax highlighting)
- JavaScript (`.js`)
- Python (`.py`)
- Java (`.java`)
- C# (`.cs`)
- C++ (`.cpp`, `.c`)
- HTML (`.html`)
- CSS (`.css`)
- JSON (`.json`)
- XML (`.xml`)
- Markdown (`.md`)
- SQL (`.sql`)
- Bash (`.sh`)
- Plain text (`.txt`)

### Image Formats
- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- GIF (`.gif`)
- BMP (`.bmp`)
- WebP (`.webp`)
- SVG (`.svg`)

## Quick Start

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd clip-rewrite
```

2. Run with Docker Compose:
```bash
docker-compose up -d
```

The application will be available at `http://localhost:8000`.

### Manual Installation

1. **Prerequisites**:
   - Python 3.9+
   - pip

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Initialize database**:
```bash
python init_db.py
```

4. **Run the application**:
```bash
python main.py
```

The application will be available at `http://localhost:8000`.

## Usage

### Creating a Clip

1. **Via Web Interface**:
   - Visit the homepage
   - Paste text or upload files
   - Set expiration time (default: 24 hours)
   - Click "Create Clip"
   - Save the 4-digit access code

2. **Via API**:
```bash
# Text content
curl -X POST "http://localhost:8000/api/clips" \
  -F "content=Your text here" \
  -F "expiration_hours=24"

# File upload
curl -X POST "http://localhost:8000/api/clips" \
  -F "files=@example.txt" \
  -F "expiration_hours=48"
```

### Accessing a Clip

1. **Via Web Interface**:
   - Go to `/retrieve`
   - Enter the 4-digit access code
   - View or download content

2. **Via API**:
```bash
# Get clip info
curl "http://localhost:8000/api/clips/1234"

# Download file
curl "http://localhost:8000/api/clips/1234/download"

# Download all files as ZIP
curl "http://localhost:8000/api/clips/1234/download?download_all=true"
```

## API Endpoints

### POST `/api/clips`
Create a new clip with text content or files.

**Parameters**:
- `content` (optional): Text content
- `language` (optional): Programming language for syntax highlighting
- `expiration_hours` (optional, default: 24): Hours until expiration
- `files` (optional): Multiple files to upload

**Response**:
```json
{
  "access_code": "1234",
  "content": "Your text here",
  "language": "python",
  "filename": null,
  "filenames": null,
  "created_at": "2025-05-26T10:00:00",
  "expires_at": "2025-05-27T10:00:00",
  "is_file": false,
  "is_image": false
}
```

### GET `/api/clips/{access_code}`
Retrieve clip information.

### GET `/api/clips/{access_code}/download`
Download clip files.

**Query Parameters**:
- `filename` (optional): Download specific file
- `download_all` (optional): Download all files as ZIP
- `as_text` (optional): Force download as text file

## Configuration

### Environment Variables

- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)
- `RELOAD`: Enable auto-reload for development (default: `true`)

### Docker Configuration

The application can be configured via environment variables in `docker-compose.yml`:

```yaml
environment:
  - HOST=0.0.0.0
  - PORT=8000
  - RELOAD=false
```

## File Storage

- Files are stored in the `uploads/` directory
- Each clip gets its own subdirectory named after the access code
- Database stores metadata and file paths
- Files are automatically cleaned up when clips expire

## Database

The application uses SQLite by default with the following schema:

**Clips Table**:
- `id`: Primary key
- `access_code`: 4-digit unique code
- `content`: Text content
- `filename`: Single filename (legacy)
- `filenames`: Comma-separated list of filenames
- `file_path`: Path to file storage
- `language`: Programming language for syntax highlighting
- `created_at`: Creation timestamp
- `expires_at`: Expiration timestamp
- `is_file`: Boolean flag for file uploads
- `is_image`: Boolean flag for image files

## Development

### Project Structure

```
clip-rewrite/
├── app/
│   ├── __init__.py           # FastAPI app factory
│   ├── models/
│   │   ├── clip.py          # Database model
│   │   ├── database.py      # Database configuration
│   │   └── schemas.py       # Pydantic schemas
│   ├── routers/
│   │   ├── clips.py         # API endpoints
│   │   └── pages.py         # Web pages
│   ├── static/              # CSS, JS assets
│   └── templates/           # Jinja2 templates
├── uploads/                 # File storage
├── main.py                  # Application entry point
├── init_db.py              # Database initialization
├── requirements.txt        # Python dependencies
└── docker-compose.yml      # Docker configuration
```

### Running in Development Mode

```bash
# Enable auto-reload
export RELOAD=true
python main.py
```

### Adding New Features

1. **Database Changes**: Update `app/models/clip.py` and run migrations
2. **API Endpoints**: Add routes in `app/routers/clips.py`
3. **Web Pages**: Add templates in `app/templates/` and routes in `app/routers/pages.py`
4. **Frontend**: Update templates and static assets

## Dependencies

- **FastAPI**: Web framework
- **SQLAlchemy**: Database ORM
- **Jinja2**: Template engine
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **python-multipart**: File upload support
- **aiofiles**: Async file operations
- **Pygments**: Syntax highlighting

## License

This project is open source. Please check the license file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Check existing issues in the repository
- Create a new issue with detailed information
- Include logs and error messages when reporting bugs
