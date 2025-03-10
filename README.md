# YouTube Video Downloader

A modern, user-friendly web application for downloading YouTube videos in various qualities, including 4K, HD, and audio-only formats. Built with Flask and yt-dlp, featuring a YouTube-inspired dark theme and real-time download progress tracking.

[Add a screenshot of your application here]

## 🚀 Development Journey

I created this project to solve the common need for a reliable YouTube video downloader with a modern interface. Here's how I built it:

### Backend Development (Flask + yt-dlp)
1. Set up a Flask application structure
2. Integrated yt-dlp for video information extraction
3. Implemented video format processing and quality selection
4. Added real-time download progress tracking using Server-Sent Events
5. Created robust error handling for various scenarios

### Frontend Development (HTML + CSS + JavaScript)
1. Designed a YouTube-inspired dark theme interface
2. Implemented responsive design for mobile devices
3. Created dynamic video information display
4. Added quality badges and format details
5. Developed a centered modal for download progress
6. Implemented real-time progress updates

### Key Technical Decisions
- Used **Flask** for its simplicity and efficiency
- Chose **yt-dlp** over youtube-dl for better reliability
- Implemented **Server-Sent Events** for real-time progress
- Used **Bootstrap 5** for responsive design
- Added **Font Awesome** for modern icons
- Implemented **async/await** for smooth API calls

## ✨ Features

- 🎥 Download YouTube videos in multiple qualities (4K, 2K, 1080p, 720p, 480p)
- 🎵 Extract audio in high-quality MP3 format (320kbps)
- 🎨 YouTube-inspired dark theme interface
- 📱 Mobile-first responsive design
- ⚡ Real-time download progress with speed and ETA
- 🖼️ Video preview with thumbnail and metadata
- ✨ Modern UI with quality badges and format details

## 🛠️ Tech Stack

- **Backend**: Python 3.8+, Flask 3.0.2
- **Video Processing**: yt-dlp 2024.3.10, FFmpeg
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5.3
- **Icons**: Font Awesome 6.0

## 📋 Requirements

```plaintext
Flask==3.0.2
Werkzeug==3.0.1
yt-dlp==2024.3.10
ffmpeg-python==0.2.0
requests==2.31.0
urllib3==2.2.1
click==8.1.7
colorama==0.4.6
blinker==1.7.0
itsdangerous==2.1.2
Jinja2==3.1.3
MarkupSafe==2.1.5
```

Plus FFmpeg installation (see installation instructions below)

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/Arunkumar6522/youtube-downloader.git
cd youtube-downloader
```

2. Create a virtual environment and activate it:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Install FFmpeg:

**Windows:**
- Download from: https://github.com/BtbN/FFmpeg-Builds/releases
- Get the file: `ffmpeg-master-latest-win64-gpl.zip`
- Extract to the project folder so you have: `ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe`

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

## 📱 Usage

1. Start the application:
```bash
python app.py
```

2. Open your web browser and go to:
```
http://localhost:5000
```

3. Paste a YouTube video URL and click "Get Video"

4. Select your preferred quality/format and click Download

## 🎯 Features in Detail

### 🎥 Video Downloads
- Multiple quality options up to 4K (if available)
- Shows file size, fps, and format details
- Combined video and audio in MP4 format
- Automatic format selection based on quality

### 🎵 Audio Downloads
- High-quality MP3 extraction (320kbps)
- Shows bitrate and file size
- Best audio stream selection
- Fast conversion process

### ⚡ Progress Tracking
- Real-time download progress
- Download speed monitoring
- Estimated time remaining
- File size tracking
- Centered modal display

### 🎨 User Interface
- Dark theme matching YouTube's design
- Mobile-responsive layout
- Quality badges (4K, HD, etc.)
- Centered modal for download progress
- Error handling with user-friendly messages
- Smooth animations and transitions

## 📁 Project Structure

```
youtube-downloader/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Documentation
├── LICENSE               # MIT License
├── .gitignore           # Git ignore rules
├── downloads/            # Download directory (created automatically)
└── templates/
    └── index.html        # Frontend template
```

## 🔧 Error Handling

The application handles various scenarios:
- Invalid URLs with clear error messages
- Private or unavailable videos
- Network connection issues
- Download failures with retry options
- Missing FFmpeg installation
- Progress tracking errors

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for reliable video extraction
- [Flask](https://flask.palletsprojects.com/) for the lightweight web framework
- [Bootstrap](https://getbootstrap.com/) for responsive UI components
- [Font Awesome](https://fontawesome.com/) for beautiful icons

## 💡 Future Improvements

- [ ] Add playlist support
- [ ] Implement user preferences storage
- [ ] Add more video platforms support
- [ ] Create a dark/light theme toggle
- [ ] Add download queue management
- [ ] Implement download resume capability

## 🆘 Support

If you encounter any issues or have questions, please [open an issue](https://github.com/Arunkumar6522/youtube-downloader/issues).

## 🔗 Connect with Me

- GitHub: [Arunkumar6522](https://github.com/Arunkumar6522)
- LinkedIn: [Add your LinkedIn profile URL]
- Portfolio: [Add your portfolio website if you have one]

## 📸 Screenshots

### Home Page
![Home Page](screenshots/home.png)

### Video Information
![Video Info](screenshots/video-info.png)

### Download Progress
![Download Progress](screenshots/download-progress.png)

## 📝 How I Built This

1. **Initial Setup**
   - Created Flask application structure
   - Set up virtual environment
   - Installed necessary dependencies

2. **Backend Development**
   - Implemented YouTube video info extraction using yt-dlp
   - Created routes for video info and download
   - Added real-time progress tracking using SSE
   - Implemented error handling and retry mechanisms

3. **Frontend Development**
   - Designed responsive UI with Bootstrap
   - Created YouTube-inspired dark theme
   - Implemented dynamic content loading
   - Added progress modal with real-time updates

4. **Features Implementation**
   - Added multiple video quality options
   - Implemented audio extraction
   - Created download progress tracking
   - Added file size and format information

5. **Testing & Refinement**
   - Tested with various YouTube videos
   - Improved error handling
   - Enhanced user feedback
   - Optimized download process

## 🔄 Recent Updates

- Added centered modal for download progress
- Improved error handling with clear messages
- Enhanced mobile responsiveness
- Added real-time download statistics
- Implemented retry mechanism for failed downloads

## 🤝 Want to Contribute?

I welcome contributions! Here's how you can help:

1. Report bugs and suggest features in the [issues section](https://github.com/Arunkumar6522/youtube-downloader/issues)
2. Review source code changes
3. Submit pull requests with improvements
4. Add new features you think would be useful
5. Help improve documentation

## ⭐ Show Your Support

If you find this project useful, please consider giving it a star on GitHub!

