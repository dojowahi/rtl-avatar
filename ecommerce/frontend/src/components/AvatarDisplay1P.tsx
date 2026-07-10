import { useEffect, useRef, memo, useState } from 'react';
import mpegts from 'mpegts.js';
import { Box, CircularProgress, Typography } from '@mui/material';

interface AvatarDisplay1PProps {
  status: 'idle' | 'initializing' | 'ready' | 'error';
  useVertexAI?: boolean;
}

interface MpegtsCustomLoader {
  open: (url: string, range: { from: number; to: number }) => void;
  close: () => void;
  destroy: () => void;
  abort: () => void;
  isWorking: () => boolean;
  onData?: (data: ArrayBuffer, receivedBytes: number) => void;
}

export const AvatarDisplay1P = memo(({ status, useVertexAI = true }: AvatarDisplay1PProps) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const playerRef = useRef<mpegts.Player | null>(null);
  const customLoaderRef = useRef<MpegtsCustomLoader | null>(null);
  const receivedBytesRef = useRef<number>(0);
  const [hasFirstFrame, setHasFirstFrame] = useState(false);
  const [frameUrl, setFrameUrl] = useState<string | null>(null);

  useEffect(() => {
    if (status !== 'ready') {
      setHasFirstFrame(false);
      setFrameUrl(null);
    }
  }, [status]);

  useEffect(() => {
    if (!useVertexAI || !videoRef.current) return;

    // Use mpegts custom loader logic to feed websocket chunks directly into media element buffers
    const player = mpegts.createPlayer({
      type: 'mpegts',
      isLive: true,
      url: 'custom',
    }, {
      customLoader: function(this: MpegtsCustomLoader) {
        this.open = () => {};
        this.close = () => {};
        this.destroy = () => {};
        this.abort = () => {};
        this.isWorking = () => false;
        customLoaderRef.current = this;
      } as unknown as { new(): mpegts.BaseLoader },
    });

    player.attachMediaElement(videoRef.current);
    player.load();
    playerRef.current = player;

    const handleVideoChunk = (event: Event) => {
      const base64Data = (event as CustomEvent).detail;
      if (!base64Data) return;

      try {
        if (base64Data.startsWith('/9j/') || base64Data.startsWith('iVBORw')) {
          setFrameUrl(`data:image/jpeg;base64,${base64Data}`);
          setHasFirstFrame(true);
          return;
        }

        const binaryString = atob(base64Data);
        const uint8Array = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          uint8Array[i] = binaryString.charCodeAt(i);
        }
        
        if (customLoaderRef.current?.onData) {
          customLoaderRef.current.onData(uint8Array.buffer, receivedBytesRef.current);
          receivedBytesRef.current += uint8Array.byteLength;
        }

        if (videoRef.current?.paused && status === 'ready') {
          videoRef.current.play().catch(e => {
            if (e.name !== 'AbortError') {
              console.warn('[AvatarDisplay1P] Autoplay failed:', e);
            }
          });
        }
      } catch (err) {
        console.error('[AvatarDisplay1P] Error processing video segment:', err);
      }
    };

    window.addEventListener('video-chunk-received', handleVideoChunk);

    return () => {
      window.removeEventListener('video-chunk-received', handleVideoChunk);
      if (playerRef.current) {
        playerRef.current.detachMediaElement();
        playerRef.current.destroy();
        playerRef.current = null;
      }
    };
  }, [status, useVertexAI]);


  useEffect(() => {
    if (!useVertexAI) return;
    
    const video = videoRef.current;
    if (!video) return;

    const handlePlaying = () => {
       setHasFirstFrame(true);
    };

    video.addEventListener('playing', handlePlaying);
    return () => video.removeEventListener('playing', handlePlaying);
  }, [useVertexAI]);

  return (
    <Box sx={{
      position: 'relative',
      width: '100%',
      height: '100%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      bgcolor: 'rgba(0,0,0,0.02)',
      borderRadius: 4,
      overflow: 'hidden',
      aspectRatio: '704 / 1280', 
    }}>
      {!useVertexAI && status === 'ready' ? (
        <Box sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 2,
          p: 3
        }}>
          {/* Pulsing Avatar Container */}
          <Box sx={{
            position: 'relative',
            width: 140,
            height: 140,
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 8px 30px rgba(0,0,0,0.08)',
            '&::after': {
              content: '""',
              position: 'absolute',
              width: '100%',
              height: '100%',
              borderRadius: '50%',
              border: '3px solid #1976d2',
              animation: 'ripple 1.6s infinite ease-in-out',
            },
            '@keyframes ripple': {
              '0%': {
                transform: 'scale(0.96)',
                opacity: 0.8,
              },
              '100%': {
                transform: 'scale(1.25)',
                opacity: 0,
              },
            },
          }}>
            <Box
              component="img"
              src="/assistant_avatar.png"
              alt="Assistant Avatar"
              sx={{
                width: 130,
                height: 130,
                borderRadius: '50%',
                objectFit: 'cover',
                border: '3px solid #fff',
              }}
            />
          </Box>
          <Typography variant="body2" sx={{ fontWeight: 'bold', color: 'primary.main', mt: 1 }}>
            Vera is listening...
          </Typography>
        </Box>
      ) : frameUrl ? (
        <Box
          component="img"
          src={frameUrl}
          alt="Speaking Avatar"
          sx={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            display: 'block'
          }}
        />
      ) : (
        <video
          ref={videoRef}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            display: (status === 'ready' && useVertexAI) ? 'block' : 'none'
          }}
          playsInline
        />
      )}
      
      {(status === 'initializing' || (status === 'ready' && useVertexAI && !hasFirstFrame)) && (
        <Box sx={{ 
          position: 'absolute',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 2
        }}>
          <CircularProgress size={40} />
          <Typography variant="body2" color="text.secondary">
            Connecting shopping assistant...
          </Typography>
        </Box>
      )}

      {status === 'error' && (
        <Typography color="error">
          Failed to load shopping avatar
        </Typography>
      )}
    </Box>
  );
});

AvatarDisplay1P.displayName = 'AvatarDisplay1P';
