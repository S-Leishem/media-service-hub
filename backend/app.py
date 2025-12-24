import yt_dlp
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import logging
import tempfile

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def get_ydl_opts(use_oauth=True):
    """Enhanced yt-dlp options with multiple bypass methods"""
    opts = {
        'format': 'best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': False,
        # Use mobile client to bypass restrictions
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web'],
                'player_skip': ['webpage', 'configs'],
                'skip': ['hls', 'dash']
            }
        },
        'http_headers': {
            'User-Agent': 'com.google.android.youtube/17.36.4 (Linux; U; Android 12; GB) gzip',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    }
    
    # Try OAuth2 authentication if available
    if use_oauth and os.environ.get('YOUTUBE_OAUTH'):
        opts['username'] = 'oauth2'
        opts['password'] = ''
    
    return opts

@app.route('/api/info', methods=['POST'])
def get_info():
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        logger.info(f"Fetching info for URL: {url}")
        
        # Try different extraction methods
        methods = [
            {'use_oauth': True},
            {'use_oauth': False}
        ]
        
        last_error = None
        for method in methods:
            try:
                ydl_opts = get_ydl_opts(**method)
                ydl_opts['quiet'] = True
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    response_data = {
                        'title': info.get('title'),
                        'thumbnail': info.get('thumbnail'),
                        'duration': info.get('duration'),
                        'uploader': info.get('uploader'),
                        'formats': []
                    }
                    
                    if 'formats' in info:
                        seen_formats = set()
                        for fmt in info['formats']:
                            format_key = f"{fmt.get('format_id')}_{fmt.get('ext')}"
                            if format_key not in seen_formats:
                                format_info = {
                                    'format_id': fmt.get('format_id'),
                                    'ext': fmt.get('ext'),
                                    'quality': fmt.get('format_note', 'Unknown'),
                                    'filesize': fmt.get('filesize'),
                                    'resolution': fmt.get('resolution')
                                }
                                response_data['formats'].append(format_info)
                                seen_formats.add(format_key)
                    
                    return jsonify(response_data)
                    
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Method {method} failed: {last_error}")
                continue
        
        # If all methods fail
        return jsonify({'error': f'All extraction methods failed. Last error: {last_error}'}), 500
            
    except Exception as e:
        logger.error(f"Error fetching info: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['POST'])
def download():
    try:
        data = request.json
        url = data.get('url')
        format_id = data.get('format_id', 'best')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        logger.info(f"Downloading URL: {url} with format: {format_id}")
        
        methods = [
            {'use_oauth': True},
            {'use_oauth': False}
        ]
        
        last_error = None
        for method in methods:
            try:
                ydl_opts = get_ydl_opts(**method)
                if format_id != 'best':
                    ydl_opts['format'] = format_id
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    
                    if os.path.exists(filename):
                        logger.info(f"Download completed: {filename}")
                        response = send_file(filename, as_attachment=True)
                        # Clean up after sending
                        try:
                            os.remove(filename)
                        except:
                            pass
                        return response
                        
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Download method {method} failed: {last_error}")
                continue
        
        return jsonify({'error': f'Download failed. Last error: {last_error}'}), 500
                
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'Media Downloader API', 'version': '1.0.0'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=False, host='0.0.0.0', port=port)
