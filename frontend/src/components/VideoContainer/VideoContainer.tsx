import React, { useRef } from 'react';
import styles from './videocontainer.module.css';
import ReactPlayer from 'react-player';
import { ProcessedPanel } from '../ProcessedPanel';
import { IVideoPanel } from '../../store/videoPanel/videoPanelReducer';
import { VideoPanel } from '../VideoPanel';
import { TimestampsPanel } from '../TimestampsPanel';
import { IProcessedVideoData } from '../../store/processedVideoData/processedVideoDataReducer';

interface IVideoContainerProps {
  videoPanel: IVideoPanel;
  processedVideoData: IProcessedVideoData[];
}

export function VideoContainer({ videoPanel, processedVideoData }: IVideoContainerProps) {
  const playerRef = useRef<ReactPlayer>(null);

  const handleSeek = (seconds: number) => {
    if (playerRef.current) {
      playerRef.current.seekTo(seconds);
    }
  };

  return (
    <div className={styles.container}>
      <ProcessedPanel processedVideoData={processedVideoData}  />
      <VideoPanel videoPanel={videoPanel} playerRef={playerRef} />
      <TimestampsPanel videoPanel={videoPanel} onTimestampClick={handleSeek} />
    </div>
  );
}
