import React from 'react';
import styles from './timestamps.module.css';
import { IVideoPanel } from '../../store/videoPanel/videoPanelReducer';
import { secondsToMinutes } from '../../utils/secondsToMinutes';

interface ITimestampsPanelProps {
  videoPanel: IVideoPanel;
  onTimestampClick: (seconds: number) => void;
}

export function TimestampsPanel({ videoPanel, onTimestampClick }: ITimestampsPanelProps) {
  return (
    <div className={styles.container}>
      <h3 className={styles.title}>Нарушения</h3>
      <ul className={styles.list}>
        {videoPanel.timestamps.map((timestamp, index) => 
          <li key={index} className={styles.item} onClick={() => onTimestampClick(timestamp.time_in_seconds)}>
            <span className={styles.timestamp}>
              {secondsToMinutes(timestamp.time_in_seconds)}
            </span>
          </li>
        )}
      </ul>
    </div>
  );
}
