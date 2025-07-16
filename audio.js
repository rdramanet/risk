/**
 * Audio System for Risk Game
 * Programmatically generates music and sound effects using Web Audio API
 */

class AudioSystem {
    constructor() {
        this.audioContext = null;
        this.masterVolume = 0.3;
        this.musicVolume = 1;
        this.sfxVolume = 0.7;
        this.isInitialized = false;
        this.currentBGM = null;
        this.musicLoopId = null;
    }

    async initialize() {
        if (this.isInitialized) return;
        
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // Resume context if suspended (required for user interaction)
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }
            
            this.isInitialized = true;
            console.log('Audio system initialized');
            
            // Start background music
            this.playBackgroundMusic();
            
        } catch (error) {
            console.error('Failed to initialize audio system:', error);
        }
    }

    // Generate a tone with specified frequency, duration, and type
    generateTone(frequency, duration, type = 'sine', volume = 1.0) {
        if (!this.isInitialized) return;

        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.value = frequency;
        oscillator.type = type;
        
        // Apply volume with fade in/out
        const totalVolume = volume * this.sfxVolume * this.masterVolume;
        gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(totalVolume, this.audioContext.currentTime + 0.01);
        gainNode.gain.linearRampToValueAtTime(0, this.audioContext.currentTime + duration);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + duration);
        
        return { oscillator, gainNode };
    }

    // Generate white noise
    generateNoise(duration, volume = 1.0) {
        if (!this.isInitialized) return;

        const bufferSize = this.audioContext.sampleRate * duration;
        const buffer = this.audioContext.createBuffer(1, bufferSize, this.audioContext.sampleRate);
        const data = buffer.getChannelData(0);
        
        for (let i = 0; i < bufferSize; i++) {
            data[i] = Math.random() * 2 - 1;
        }
        
        const source = this.audioContext.createBufferSource();
        const gainNode = this.audioContext.createGain();
        
        source.buffer = buffer;
        source.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        const totalVolume = volume * this.sfxVolume * this.masterVolume;
        gainNode.gain.setValueAtTime(totalVolume, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + duration);
        
        source.start(this.audioContext.currentTime);
        
        return { source, gainNode };
    }

    // Play attack sound effect
    playAttackSound() {
        if (!this.isInitialized) return;
        
        // Explosive attack sound with multiple frequencies
        setTimeout(() => this.generateTone(150, 0.1, 'sawtooth', 0.8), 0);
        setTimeout(() => this.generateTone(120, 0.15, 'square', 0.6), 50);
        setTimeout(() => this.generateNoise(0.2, 0.4), 100);
        setTimeout(() => this.generateTone(80, 0.3, 'triangle', 0.5), 150);
    }

    // Play victory sound effect
    playVictorySound() {
        if (!this.isInitialized) return;
        
        // Triumphant ascending chord
        const notes = [261.63, 329.63, 392.00, 523.25]; // C4, E4, G4, C5
        notes.forEach((freq, index) => {
            setTimeout(() => {
                this.generateTone(freq, 0.5, 'sine', 0.6);
            }, index * 100);
        });
    }

    // Play defeat sound effect
    playDefeatSound() {
        if (!this.isInitialized) return;
        
        // Descending sad trombone effect
        const startFreq = 220;
        const endFreq = 110;
        const duration = 1.0;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.type = 'sawtooth';
        oscillator.frequency.setValueAtTime(startFreq, this.audioContext.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(endFreq, this.audioContext.currentTime + duration);
        
        const volume = 0.4 * this.sfxVolume * this.masterVolume;
        gainNode.gain.setValueAtTime(volume, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + duration);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + duration);
    }

    // Play army placement sound
    playPlacementSound() {
        if (!this.isInitialized) return;
        
        // Quick upward chirp
        this.generateTone(400, 0.1, 'sine', 0.3);
        setTimeout(() => this.generateTone(600, 0.1, 'sine', 0.2), 50);
    }

    // Play turn change sound
    playTurnChangeSound() {
        if (!this.isInitialized) return;
        
        // Bell-like chime
        this.generateTone(800, 0.3, 'sine', 0.4);
        setTimeout(() => this.generateTone(1000, 0.2, 'sine', 0.3), 100);
    }

    // Play continent bonus sound
    playBonusSound() {
        if (!this.isInitialized) return;
        
        // Magical sparkle effect
        const frequencies = [523, 659, 784, 1047, 1319]; // C5, E5, G5, C6, E6
        frequencies.forEach((freq, index) => {
            setTimeout(() => {
                this.generateTone(freq, 0.3, 'sine', 0.5);
            }, index * 80);
        });
    }

    // Play error/invalid action sound
    playErrorSound() {
        if (!this.isInitialized) return;
        
        // Buzzer sound
        this.generateTone(150, 0.2, 'square', 0.5);
        setTimeout(() => this.generateTone(100, 0.3, 'square', 0.4), 100);
    }

    // Play button click sound
    playClickSound() {
        if (!this.isInitialized) return;
        
        // Quick click
        this.generateTone(1000, 0.05, 'square', 0.2);
    }

    // Generate background music
    playBackgroundMusic() {
        if (!this.isInitialized) return;
        
        const playMelody = () => {
            // Epic orchestral-style melody
            const melody = [
                {freq: 261.63, duration: 0.5}, // C4
                {freq: 293.66, duration: 0.5}, // D4
                {freq: 329.63, duration: 0.5}, // E4
                {freq: 392.00, duration: 1.0}, // G4
                {freq: 329.63, duration: 0.5}, // E4
                {freq: 293.66, duration: 0.5}, // D4
                {freq: 261.63, duration: 1.0}, // C4
                {freq: 246.94, duration: 0.5}, // B3
                {freq: 261.63, duration: 0.5}, // C4
                {freq: 329.63, duration: 1.0}, // E4
                {freq: 392.00, duration: 1.5}, // G4
            ];
            
            let currentTime = 0;
            melody.forEach(note => {
                setTimeout(() => {
                    if (this.currentBGM) { // Check if music should still be playing
                        this.generateTone(note.freq, note.duration, 'triangle', 0.15 * this.musicVolume);
                        // Add harmony
                        this.generateTone(note.freq * 1.5, note.duration, 'sine', 0.1 * this.musicVolume);
                    }
                }, currentTime * 1000);
                currentTime += note.duration;
            });
            
            // Schedule next iteration
            if (this.currentBGM) {
                this.musicLoopId = setTimeout(playMelody, (currentTime + 2) * 1000);
            }
        };
        
        this.currentBGM = true;
        playMelody();
    }

    // Stop background music
    stopBackgroundMusic() {
        this.currentBGM = false;
        if (this.musicLoopId) {
            clearTimeout(this.musicLoopId);
            this.musicLoopId = null;
        }
    }

    // Set master volume (0.0 to 1.0)
    setMasterVolume(volume) {
        this.masterVolume = Math.max(0, Math.min(1, volume));
    }

    // Set music volume (0.0 to 1.0)
    setMusicVolume(volume) {
        this.musicVolume = Math.max(0, Math.min(1, volume));
    }

    // Set sound effects volume (0.0 to 1.0)
    setSFXVolume(volume) {
        this.sfxVolume = Math.max(0, Math.min(1, volume));
    }

    // Mute/unmute all audio
    setMute(muted) {
        if (muted) {
            this.setMasterVolume(0);
            this.stopBackgroundMusic();
        } else {
            this.setMasterVolume(0.3);
            this.playBackgroundMusic();
        }
    }

    // Clean up resources
    dispose() {
        this.stopBackgroundMusic();
        if (this.audioContext) {
            this.audioContext.close();
        }
        this.isInitialized = false;
    }
}

// Create global audio system instance
window.audioSystem = new AudioSystem();

// Initialize audio on first user interaction
let audioInitialized = false;
const initAudio = async () => {
    if (!audioInitialized) {
        await window.audioSystem.initialize();
        audioInitialized = true;
        // Remove event listeners after initialization
        document.removeEventListener('click', initAudio);
        document.removeEventListener('keydown', initAudio);
        document.removeEventListener('touchstart', initAudio);
    }
};

// Add event listeners for user interaction
document.addEventListener('click', initAudio);
document.addEventListener('keydown', initAudio);
document.addEventListener('touchstart', initAudio);

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AudioSystem;
}
