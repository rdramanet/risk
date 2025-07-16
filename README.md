# Risk - Multiplayer Game

A real-time multiplayer version of the classic Risk board game built with Python WebSocket backend and JavaScript frontend. Features programmatic audio generation and comprehensive testing.

## 🚀 Quick Start

1. **Setup Environment**
   ```bash
   python test_runner.py setup
   ```

2. **Run Tests**
   ```bash
   python test_runner.py test
   ```

3. **Start Development Server**
   ```bash
   python test_runner.py server
   ```

4. **Open Game**
   - Navigate to `http://localhost:8000`
   - Create or join a multiplayer game
   - Invite friends using the Game ID

## 🎮 Game Features

### Multiplayer
- **Real-time multiplayer**: Up to 6 players via WebSocket
- **Game rooms**: Create private games with unique IDs
- **Live synchronization**: All actions synced across players
- **Turn-based gameplay**: Managed server-side turn order

### Audio System
- **Programmatic audio**: No external files needed
- **Dynamic music**: Epic orchestral background music
- **Sound effects**: Attack, victory, defeat, placement sounds
- **Audio controls**: Volume slider and mute toggle
- **Spatial audio**: Different sounds for different actions

### Original Features
- **42 territories** across 6 continents
- **Strategic gameplay**: Army placement and attacking
- **Continent bonuses**: Control entire continents for extra armies
- **AI opponents**: Single-player mode with intelligent AI
- **Beautiful SVG map**: Responsive and interactive

## 🛠 Architecture

### Backend (Python)
- **FastAPI**: Modern async web framework
- **WebSockets**: Real-time bidirectional communication
- **Game state management**: Centralized game logic
- **Player authentication**: Session-based player tracking

### Frontend (JavaScript)
- **Existing UI**: Enhanced original game interface
- **WebSocket client**: Real-time server communication
- **Web Audio API**: Programmatic sound generation
- **Responsive design**: Works on desktop and mobile

### Testing
- **Backend tests**: Comprehensive pytest suite
- **Frontend tests**: QUnit-based browser tests
- **Automatic testing**: File watcher runs tests on changes
- **CI/CD ready**: Structured for continuous integration

## 📁 Project Structure

```
.
├── server.py              # Python WebSocket server
├── index.html             # Game HTML interface
├── index.js               # Enhanced game logic
├── audio.js               # Programmatic audio system
├── scss/main.scss         # Game styling
├── test_server.py         # Backend unit tests
├── test_frontend.html     # Frontend unit tests
├── test_runner.py         # Automated test runner
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🎵 Audio Features

The game includes a sophisticated audio system that generates all sounds programmatically:

### Background Music
- Epic orchestral melody using multiple oscillators
- Harmonic layering for rich sound
- Continuous looping with smooth transitions

### Sound Effects
- **Attack**: Explosive multi-frequency burst with noise
- **Victory**: Triumphant ascending chord progression
- **Defeat**: Descending trombone-style effect
- **Army Placement**: Quick upward chirp
- **Turn Change**: Bell-like chime
- **Continent Bonus**: Magical sparkle sequence
- **Errors**: Buzzer-style warning sounds
- **UI Clicks**: Subtle click feedback

### Audio Controls
- Master volume control
- Music/SFX balance
- Mute toggle
- Persistent settings

## 🕹 How to Play

### Single Player
1. Click "Start" to begin single-player mode
2. Place armies during fortify phase
3. Attack neighboring territories during battle phase
4. End turn to let AI players move
5. Control all 42 territories to win

### Multiplayer
1. **Create Game**: Click "Create Game" to start new room
2. **Share ID**: Give the Game ID to other players
3. **Join Game**: Others click "Join Game" and enter the ID
4. **Start**: Once all players joined, click "Start Game"
5. **Play**: Take turns placing armies and attacking
6. **Win**: First player to control all territories wins

### Game Controls
- **Click territory**: Select for army placement or attack
- **Shift+Click**: Deploy all reserve armies at once
- **Attack**: Select your territory, then enemy territory
- **End Turn**: Pass control to next player
- **Audio**: Use volume slider and mute button

## 🧪 Testing

### Run All Tests
```bash
python test_runner.py test
```

### Backend Tests Only
```bash
python test_runner.py backend
```

### Frontend Tests Only
```bash
python test_runner.py frontend
```

### Continuous Testing
```bash
python test_runner.py watch
```

### Test Coverage
- **Backend**: Game logic, WebSocket handling, API endpoints
- **Frontend**: Audio system, UI controls, game state management
- **Integration**: WebSocket message flow, multiplayer synchronization

## 🔧 Development

### File Watching
The test runner includes automatic file watching:
```bash
python test_runner.py watch
```

This will:
- Run all tests immediately
- Watch for changes in `.py`, `.js`, and `.html` files
- Automatically re-run tests when files change
- Provide instant feedback during development

### Adding Tests

#### Backend Tests
Add test methods to `test_server.py`:
```python
def test_your_feature(self):
    # Test implementation
    assert expected == actual
```

#### Frontend Tests
Add test cases to `test_frontend.html`:
```javascript
QUnit.test('Your test name', function(assert) {
    // Test implementation
    assert.equal(expected, actual, 'Test description');
});
```

### Environment Setup

The development environment requires:
- Python 3.7+
- Modern web browser with WebSocket support
- Internet connection for QUnit CDN (frontend tests)

All Python dependencies are automatically installed via:
```bash
python test_runner.py setup
```

## 🚀 Deployment

### Production Server
```bash
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Run tests: `python test_runner.py test`
4. Commit changes: `git commit -am 'Add feature'`
5. Push branch: `git push origin feature-name`
6. Create Pull Request

## 📝 License

This project enhances the original Risk game implementation with multiplayer capabilities and audio features while maintaining compatibility with the existing codebase.

## 🎯 Features Implemented

✅ **Multiplayer with Python backend**
- WebSocket-based real-time communication
- Game room creation and joining
- Turn-based multiplayer logic
- Player synchronization

✅ **Programmatic audio system**
- Web Audio API integration
- Dynamic music generation
- Comprehensive sound effects
- Volume controls

✅ **Existing UI preservation**
- Enhanced original HTML/CSS/JS
- Added multiplayer controls
- Maintained game aesthetics
- Responsive design

✅ **Comprehensive testing**
- Backend unit tests with pytest
- Frontend tests with QUnit
- Automatic test runner
- File watching for continuous testing

✅ **Development workflow**
- One-command setup
- Automatic dependency management
- Real-time test feedback
- Production-ready server

The game maintains full backward compatibility with single-player mode while adding robust multiplayer capabilities, audio features, and comprehensive testing infrastructure.
