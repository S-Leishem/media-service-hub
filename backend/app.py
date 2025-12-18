from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import json
from pathlib import Path
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Media Downloader API',
        'version': '1.0.0',
        'endpoints': {
            'info': '/api/info',
            'download': '/api/download',
            'health': '/health'
        }
    }), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

# Create downloads folder
DOWNLOAD_FOLDER = Path('downloads')
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

def get_media_info(url):
    """
    Fetch media information from the URL using yt-dlp
    """
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Extract formats
            formats = []
            if 'formats' in info:
                # Group formats by quality
                seen_resolutions = set()
                for fmt in info['formats']:
                    if fmt.get('vcodec') != 'none' or fmt.get('acodec') != 'none':
                        resolution = fmt.get('format_note', 'Unknown')
                        if resolution not in seen_resolutions:
                            seen_resolutions.add(resolution)
                            formats.append({
                                'format_id': fmt['format_id'],
                                'quality': resolution,
                                'resolution': f"{fmt.get('width', 0)}x{fmt.get('height', 0)}" if fmt.get('height') else 'Unknown',
                                'format': fmt.get('ext', 'mp4'),
                                'filesize': fmt.get('filesize', 'Unknown')
                            })
            
            # Get platform
            platform = 'Unknown'
            if 'youtube.com' in url or 'youtu.be' in url:
                platform = 'YouTube'
            elif 'instagram.com' in url:
                platform = 'Instagram'
            
            return {
                'url': url,
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'upload_date': info.get('upload_date', 'Unknown'),
                'thumbnail': info.get('thumbnail'),
                'platform': platform,
                'formats': formats[:10],  # Limit to top 10 formats
                'ext': info.get('ext', 'mp4')
            }
    
    except Exception as e:
        logger.error(f"Error getting media info: {str(e)}")
        raise Exception(f"Failed to fetch media information: {str(e)}")

def download_media(url, format_id=None):
    """
    Download media from the URL
    """
    ydl_opts = {
        'format': format_id or 'best',
        'outtmpl': str(DOWNLOAD_FOLDER / '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'socket_timeout': 30,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    
    except Exception as e:
        logger.error(f"Error downloading media: {str(e)}")
        raise Exception(f"Failed to download media: {str(e)}")

@app.route('/api/info', methods=['POST'])
def get_info():
    """
    API endpoint to get media information
    """
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Validate URL
        try:
            urlparse(url)
        except:
            return jsonify({'error': 'Invalid URL format'}), 400
        
        # Check if it's a supported platform
        if not ('youtube.com' in url or 'youtu.be' in url or 'instagram.com' in url):
            return jsonify({'error': 'Unsupported platform. Please use YouTube or Instagram'}), 400
        
        info = get_media_info(url)
        return jsonify(info), 200
    
    except Exception as e:
        logger.error(f"Error in /api/info: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/download', methods=['POST'])
def download():
    """
    API endpoint to download media
    """
    try:
        data = request.get_json()
        url = data.get('url')
        format_id = data.get('format_id', 'best')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Download the media
        filepath = download_media(url, format_id)
        
        # Send file to user
        return send_file(
            filepath,
            as_attachment=True,
            download_name=Path(filepath).name
        )
    
    except Exception as e:
        logger.error(f"Error in /api/download: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=False, host='0.0.0.0', port=port)
