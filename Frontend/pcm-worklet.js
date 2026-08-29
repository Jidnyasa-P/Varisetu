/**
 * VariSetu AudioWorklet Processor for Realtime 16kHz Mono PCM16 Streaming.
 * Captures microphone audio, downsamples to 16,000 Hz, quantizes Float32 -> Int16,
 * and emits fixed-size 50ms PCM chunks (800 samples = 1,600 bytes).
 */

class PcmProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.targetSampleRate = 16000;
    this.bufferSize = 800; // 50ms at 16kHz
    this.pcmBuffer = new Int16Array(this.bufferSize);
    this.bufferIndex = 0;
    this.sequence = 0;
    this.isPaused = false;

    this.port.onmessage = (event) => {
      if (event.data && event.data.command === 'pause') {
        this.isPaused = true;
      } else if (event.data && event.data.command === 'resume') {
        this.isPaused = false;
      }
    };
  }

  process(inputs, outputs, parameters) {
    if (this.isPaused) return true;

    const input = inputs[0];
    if (!input || input.length === 0) return true;

    const channelData = input[0]; // Mono or primary channel
    if (!channelData || channelData.length === 0) return true;

    const inputSampleRate = sampleRate; // Global in AudioWorkletGlobalScope

    if (inputSampleRate === this.targetSampleRate) {
      for (let i = 0; i < channelData.length; i++) {
        let sample = Math.max(-1.0, Math.min(1.0, channelData[i]));
        this.pcmBuffer[this.bufferIndex++] = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;

        if (this.bufferIndex >= this.bufferSize) {
          this.flushBuffer();
        }
      }
    } else {
      // Linear interpolation downsampling to 16kHz
      const ratio = inputSampleRate / this.targetSampleRate;
      let srcIndex = 0;

      while (srcIndex < channelData.length) {
        const i1 = Math.floor(srcIndex);
        const i2 = Math.min(i1 + 1, channelData.length - 1);
        const frac = srcIndex - i1;
        const interpolated = channelData[i1] * (1.0 - frac) + channelData[i2] * frac;

        let sample = Math.max(-1.0, Math.min(1.0, interpolated));
        this.pcmBuffer[this.bufferIndex++] = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;

        if (this.bufferIndex >= this.bufferSize) {
          this.flushBuffer();
        }

        srcIndex += ratio;
      }
    }

    return true;
  }

  flushBuffer() {
    const chunkCopy = new Int16Array(this.pcmBuffer);
    this.port.postMessage({
      type: 'pcm16_chunk',
      sequence: this.sequence++,
      timestamp: Date.now(),
      sampleRate: this.targetSampleRate,
      samplesCount: this.bufferSize,
      buffer: chunkCopy.buffer
    }, [chunkCopy.buffer]);

    this.bufferIndex = 0;
  }
}

registerProcessor('pcm-processor', PcmProcessor);
