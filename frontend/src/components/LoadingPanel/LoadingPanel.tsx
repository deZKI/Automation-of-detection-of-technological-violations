import React from 'react';
import styles from './loadingpanel.module.css';
import {LoadingList} from './LoadingList';
import {LoadingButton} from './LoadingButton';
import {IUploadedVideo} from '../../hooks/useUploadedVideos';

interface ILoadingPanelProps {
  uploadedVideos: IUploadedVideo[];
}

export function LoadingPanel({ uploadedVideos }: ILoadingPanelProps) {
  return (
    <div className={styles.container}>
      <LoadingList uploadedVideos={uploadedVideos} />
      <LoadingButton />
    </div>
  );
}
