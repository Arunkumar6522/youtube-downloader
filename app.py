from flask import Flask, render_template, request, send_file, jsonify, Response
import yt_dlp
import os
import time
import logging
import json
from threading import Thread
from queue import Queue
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('youtube_downloader')

# Create downloads directory if it doesn't exist
DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

# Update the FFmpeg paths
ffmpeg_locations = [
    '/usr/bin',  # Linux system path
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg-master-latest-win64-gpl', 'bin'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ffmpeg-master-latest-win64-gpl', 'bin'),
    r'C:\ffmpeg-master-latest-win64-gpl\bin',
    ''
]

def get_video_info(url):
    """Get YouTube video information including available formats"""
    try:
        logger.info(f"Fetching video info for URL: {url}")
        
        # Clean and validate URL
        if 'youtu.be' in url:
            # Convert youtu.be URL to full URL
            video_id = url.split('/')[-1].split('?')[0]
            url = f'https://www.youtube.com/watch?v={video_id}'
        elif 'youtube.com' in url:
            # Ensure it's a watch URL
            if '/watch?v=' not in url:
                if '/shorts/' in url:
                    video_id = url.split('/shorts/')[-1].split('?')[0]
                    url = f'https://www.youtube.com/watch?v={video_id}'
                else:
                    logger.error("Not a valid YouTube watch URL")
                    return None
        else:
            logger.error("Invalid YouTube URL")
            return None
            
        logger.info(f"Processed URL: {url}")
        
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'format': 'best',  # Default format for extraction
            'no_check_certificates': True,  # Skip HTTPS certificate validation
            'ignoreerrors': False,  # Don't ignore errors during extraction
            'no_playlist': True,  # Only download single video even if URL is a playlist
            'extract_flat': False,
            'youtube_include_dash_manifest': True,
            'youtube_include_hls_manifest': True,
            'allow_unplayable_formats': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info("Extracting video info...")
                try:
                    # First try to extract basic info
                    basic_info = ydl.extract_info(url, download=False, process=False)
                    if not basic_info:
                        logger.error("Could not extract basic video info")
                        return None
                        
                    logger.info(f"Basic info extracted - Title: {basic_info.get('title', 'Unknown')}")
                    
                    # Then extract full info
                    video_info = ydl.extract_info(url, download=False)
                    if not video_info:
                        logger.error("Could not extract full video info")
                        return None
                        
                except yt_dlp.utils.ExtractorError as e:
                    logger.error(f"Extraction error: {str(e)}")
                    return None
                except yt_dlp.utils.DownloadError as e:
                    logger.error(f"Download error: {str(e)}")
                    return None
                
                logger.info(f"Successfully extracted info for video: {video_info.get('title', 'Unknown')}")
                
                # Prepare formats list
                formats = {'video': [], 'audio': []}
                seen_qualities = set()  # To track unique quality combinations
                
                # Get all available formats
                available_formats = video_info.get('formats', [])
                logger.info(f"Found {len(available_formats)} available formats")
                
                if not available_formats:
                    logger.error("No formats found in video info")
                    return None
                
                # Find best audio format
                best_audio = None
                best_audio_bitrate = 0
                for f in available_formats:
                    if f.get('vcodec', 'none') == 'none' and f.get('acodec', 'none') != 'none':
                        abr = f.get('abr', 0)
                        if abr > best_audio_bitrate:
                            best_audio = f
                            best_audio_bitrate = abr

                # Process available formats
                for f in available_formats:
                    format_id = f.get('format_id', '')
                    ext = f.get('ext', '')
                    filesize = f.get('filesize')  # Don't provide default to handle None case
                    vcodec = f.get('vcodec', 'none')
                    acodec = f.get('acodec', 'none')
                    
                    logger.debug(f"Processing format: {format_id} - {ext} - {vcodec} - {acodec}")
                    
                    # Skip formats without video
                    if vcodec == 'none' or not format_id:
                        continue

                    height = f.get('height', 0)
                    fps = f.get('fps', 0)
                    
                    # Skip non-video formats
                    if not height:
                        continue

                    # Create quality label
                    if height >= 2160:
                        quality = "4K"
                        quality_order = 5
                    elif height >= 1440:
                        quality = "2K"
                        quality_order = 4
                    elif height >= 1080:
                        quality = "1080p HD"
                        quality_order = 3
                    elif height >= 720:
                        quality = "720p HD"
                        quality_order = 2
                    elif height >= 480:
                        quality = "480p"
                        quality_order = 1
                    elif height >= 360:
                        quality = "360p"
                        quality_order = 0
                    else:
                        continue  # Skip lower qualities

                    # Create unique key for this quality
                    quality_key = f"{height}_{fps}"
                    
                    if quality_key not in seen_qualities:
                        seen_qualities.add(quality_key)
                        
                        # Calculate combined size if we need to add audio
                        total_filesize = filesize
                        if acodec == 'none' and best_audio:
                            audio_size = best_audio.get('filesize', 0)
                            if filesize is not None and audio_size is not None:
                                total_filesize = filesize + audio_size
                        
                        # If format has both video and audio, use it directly
                        if acodec != 'none':
                            format_string = format_id
                        else:
                            # If no audio, combine with best audio
                            format_string = f"{format_id}+bestaudio[ext=m4a]/bestaudio"
                        
                        format_info = {
                            'format_id': format_string,
                            'ext': 'mp4',  # Force MP4 output
                            'quality': quality,
                            'quality_order': quality_order,
                            'fps': fps if fps > 30 else None,  # Only show fps if higher than 30
                            'filesize_mb': round(total_filesize / (1024 * 1024), 1) if total_filesize is not None else None,
                            'height': height,  # Store height for exact matching
                            'vcodec': vcodec,  # Store video codec
                            'acodec': acodec,  # Store audio codec
                            'tbr': f.get('tbr', 0),  # Total bitrate
                            'vbr': f.get('vbr', 0),  # Video bitrate
                            'abr': f.get('abr', 0)   # Audio bitrate
                        }
                        formats['video'].append(format_info)
                        logger.info(f"Added format: {quality} ({height}p) {'with' if acodec != 'none' else 'without'} audio - Size: {format_info['filesize_mb']}MB")

                # Add audio option
                if best_audio:
                    audio_filesize = best_audio.get('filesize')
                    format_info = {
                        'format_id': best_audio['format_id'],
                        'bitrate': f"{int(best_audio.get('abr', 0))}kbps",
                        'filesize_mb': round(audio_filesize / (1024 * 1024), 1) if audio_filesize is not None else None
                    }
                    formats['audio'].append(format_info)
                    logger.info(f"Added audio format: {format_info['bitrate']}")
                
                # Sort formats by quality
                formats['video'].sort(key=lambda x: (x.get('quality_order', 0), x.get('fps', 0) or 0), reverse=True)
                
                if not formats['video'] and not formats['audio']:
                    logger.error("No valid formats found after processing")
                    return None
                
                # Prepare response
                info = {
                    'title': video_info.get('title', 'Untitled'),
                    'channel': video_info.get('uploader', 'Unknown'),
                    'duration': video_info.get('duration', 0),
                    'thumbnail': video_info.get('thumbnail', ''),
                    'views': video_info.get('view_count', 0),
                    'description': video_info.get('description', ''),
                    'upload_date': video_info.get('upload_date', ''),
                    'formats': formats
                }
                
                logger.info(f"Successfully prepared info with {len(formats['video'])} video formats and {len(formats['audio'])} audio formats")
                return info
                
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"YouTube-DL error: {str(e)}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting video info: {str(e)}")
        return None

def progress_queue_reader(queue, event_id):
    """Generator function to yield progress events"""
    while True:
        data = queue.get()
        if data is None:  # Signal to stop
            break
        yield f"id: {event_id}\ndata: {json.dumps(data)}\n\n"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-info', methods=['POST'])
def get_info():
    try:
        url = request.form.get('url')
        if not url:
            return jsonify({
                'success': False,
                'message': 'Please enter a YouTube URL'
            })
            
        # Basic URL validation
        if 'youtu.be' not in url and 'youtube.com' not in url:
            return jsonify({
                'success': False,
                'message': 'Please enter a valid YouTube URL (e.g., https://www.youtube.com/watch?v=... or https://youtu.be/...)'
            })
        
        info = get_video_info(url)
        
        if not info:
            # Check if URL is a shorts URL
            if 'shorts' in url:
                return jsonify({
                    'success': False,
                    'message': 'YouTube Shorts are currently not supported. Please use regular YouTube video URLs.'
                })
            # Check if URL is a playlist
            elif 'playlist' in url or 'list=' in url:
                return jsonify({
                    'success': False,
                    'message': 'Playlists are not supported. Please enter a single video URL.'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Could not get video information. Please make sure:\n1. The video URL is correct\n2. The video exists and is not private\n3. The video is available in your country'
                })
        
        return jsonify({
            'success': True,
            'info': info
        })
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in get_info route: {error_msg}")
        
        if "Video unavailable" in error_msg:
            message = "This video is unavailable. It might be private or deleted."
        elif "Sign in" in error_msg:
            message = "This video requires age verification or sign-in to access."
        elif "copyright" in error_msg.lower():
            message = "This video is not available due to copyright restrictions."
        else:
            message = "An error occurred while fetching video information. Please try again."
            
        return jsonify({
            'success': False,
            'message': message
        })

@app.route('/download-progress')
def download_progress():
    url = request.args.get('url')
    format_id = request.args.get('format')
    type = request.args.get('type', 'video')
    
    if not url:
        return jsonify({'success': False, 'message': 'URL is required'})
    
    # Create a queue for progress updates
    progress_queue = Queue()
    event_id = int(time.time() * 1000)  # Unique ID for this download
    
    def download_thread():
        try:
            # Start the download
            filename, error = download_video(url, format_id, type, progress_queue)
            
            if error:
                progress_queue.put({
                    'status': 'error',
                    'message': error
                })
            else:
                progress_queue.put({
                    'status': 'complete',
                    'filename': filename,
                    'download_url': f'/get-file/{filename}'
                })
        except Exception as e:
            progress_queue.put({
                'status': 'error',
                'message': str(e)
            })
        finally:
            progress_queue.put(None)  # Signal to stop the event stream
    
    # Start download in background thread
    Thread(target=download_thread).start()
    
    return Response(
        progress_queue_reader(progress_queue, event_id),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )

def download_video(url, format_id=None, type='video', progress_queue=None):
    """Download video or audio in specified format with progress updates"""
    try:
        timestamp = int(time.time())
        filename = f"youtube_{timestamp}"
        
        # Update the output template to use DOWNLOADS_DIR
        output_template = os.path.join(DOWNLOADS_DIR, f'{filename}.%(ext)s')

        def progress_hook(d):
            if d['status'] == 'downloading' and progress_queue:
                try:
                    total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                    downloaded = d.get('downloaded_bytes', 0)
                    speed = d.get('speed', 0)
                    
                    if total and downloaded:
                        percent = (downloaded / total) * 100
                        eta = d.get('eta', 0)
                        
                        progress_queue.put({
                            'status': 'downloading',
                            'percent': round(percent, 1),
                            'speed': format_bytes(speed) if speed else '--',
                            'downloaded': format_bytes(downloaded),
                            'total': format_bytes(total),
                            'eta': format_time(eta) if eta else '--'
                        })
                        
                except Exception as e:
                    logger.error(f"Error in progress hook: {str(e)}")
            
        ydl_opts = {
            'format': format_id if format_id else 'bestvideo+bestaudio/best',
            'outtmpl': output_template,
            'ffmpeg_location': None,  # Will be set below
            'progress_hooks': [progress_hook],
            'merge_output_format': 'mp4',
            'quiet': False,
            'no_warnings': True,
            'format_sort': [
                'res',
                'fps',
                'codec:h264',
                'size',
                'br',
                'asr',
                'proto'
            ],
            'postprocessors': [{
                'key': 'FFmpegVideoRemuxer',
                'preferedformat': 'mp4',
            }]
        }

        # Find FFmpeg
        for location in ffmpeg_locations:
            ffmpeg_path = os.path.join(location, 'ffmpeg') if location else 'ffmpeg'
            if os.path.exists(ffmpeg_path) or location == '':
                ydl_opts['ffmpeg_location'] = location
                logger.info(f"Found FFmpeg at: {ffmpeg_path}")
                break

        if type == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
            })
            filename = f"{filename}.mp3"
        else:
            # For video, ensure we get the exact format requested
            if format_id:
                # If format_id contains a plus (combined format), keep it as is
                if '+' not in format_id:
                    # Otherwise, ensure we get audio
                    ydl_opts['format'] = f"{format_id}+bestaudio[ext=m4a]/bestaudio"
                # Add format-specific options
                ydl_opts.update({
                    'merge_output_format': 'mp4',
                    'postprocessors': [{
                        'key': 'FFmpegVideoRemuxer',
                        'preferedformat': 'mp4',
                    }]
                })
            filename = f"{filename}.mp4"
            
        logger.info(f"Starting download with format: {ydl_opts['format']}")
        logger.info(f"Using FFmpeg from: {ffmpeg_path}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # First verify the format is available
                info = ydl.extract_info(url, download=False)
                if not info:
                    return None, "Could not verify video format"
                    
                # Then download
                error_code = ydl.download([url])
                if error_code != 0:
                    raise Exception("Download failed with error code: " + str(error_code))
                    
            except Exception as e:
                logger.error(f"Download error: {str(e)}")
                return None, f"Download error: {str(e)}"
            
        # Find the downloaded file
        downloaded_file = None
        for file in os.listdir(DOWNLOADS_DIR):
            if file.startswith(os.path.basename(filename).split('.')[0]):
                downloaded_file = file
                break
                
        if not downloaded_file:
            return None, "Download failed - file not found"
            
        # Verify file size
        file_path = os.path.join(DOWNLOADS_DIR, downloaded_file)
        actual_size = os.path.getsize(file_path)
        actual_size_mb = actual_size / (1024 * 1024)
        
        logger.info(f"Downloaded file size: {actual_size_mb:.1f}MB")
        
        if actual_size_mb < 1:  # If file is less than 1MB, something went wrong
            os.remove(file_path)  # Clean up the small file
            return None, "Download failed - file size too small, please try a different format"
            
        # Verify the file is a valid video/audio file
        try:
            import subprocess
            result = subprocess.run([
                os.path.join(ffmpeg_path, 'ffprobe.exe') if ffmpeg_path else 'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=codec_type',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                file_path
            ], capture_output=True, text=True)
            
            if result.returncode != 0 and type == 'video':
                os.remove(file_path)
                return None, "Download failed - invalid video file"
                
        except Exception as e:
            logger.error(f"Error verifying file: {str(e)}")
            
        return downloaded_file, None
                
    except Exception as e:
        error_msg = str(e)
        if "ffmpeg not found" in error_msg.lower():
            return None, (
                "FFmpeg not found. Please download FFmpeg:\n"
                "1. Download from: https://github.com/BtbN/FFmpeg-Builds/releases\n"
                "2. Get the file: ffmpeg-master-latest-win64-gpl.zip\n"
                "3. Extract to your project folder so you have: ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe"
            )
        logger.error(f"Error downloading video: {error_msg}")
        return None, error_msg

def format_bytes(bytes):
    """Format bytes to human readable string"""
    if not bytes:
        return '--'
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024
    return f"{bytes:.1f}TB"

def format_time(seconds):
    """Format seconds to human readable string"""
    if not seconds:
        return '--'
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

@app.route('/download', methods=['POST'])
def download():
    try:
        url = request.form.get('url')
        format_id = request.form.get('format')
        type = request.form.get('type', 'video')
        
        if not url:
            return jsonify({
                'success': False,
                'message': 'Please enter a YouTube URL'
            })
            
        filename, error = download_video(url, format_id, type)
        
        if error:
            return jsonify({
                'success': False,
                'message': error
            })
            
        if not filename:
            return jsonify({
                'success': False,
                'message': 'Download failed'
            })
            
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/get-file/{filename}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/get-file/<filename>')
def get_file(filename):
    try:
        filename = os.path.basename(filename)
        filepath = os.path.join(DOWNLOADS_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'message': 'File not found'
            }), 404
            
        content_type = 'video/mp4' if filename.endswith('.mp4') else 'audio/mpeg'
        
        response = send_file(
            filepath,
            mimetype=content_type,
            as_attachment=True,
            download_name=filename
        )
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host=host, port=port, debug=debug) 