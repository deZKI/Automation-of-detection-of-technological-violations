import React from 'react';
import styles from './processedpanel.module.css';
import {IProcessedVideoData} from '../../store/processedVideoData/processedVideoDataReducer';
import {ProcessedList} from './ProcessedList';
import {ProcessedPanelButton} from './ProcessedPanelButton';

interface IProcessedPanelProps {
  processedVideoData: IProcessedVideoData[];
}

export function ProcessedPanel({ processedVideoData }: IProcessedPanelProps) {
  return (
    <div className={styles.container}>
      <ProcessedList processedVideoData={processedVideoData} />
      <ProcessedPanelButton />
    </div>
  );
}
