import React from 'react';
import styles from './uploadingpage.module.css';
import {useSelector} from "react-redux";
import {IInitialState} from '../../store/reducer';
import {IProcessedVideoData} from '../../store/processedVideoData/processedVideoDataReducer';
import {useUploadedVideos} from '../../hooks/useUploadedVideos';
import {UploadingText} from './UploadingText';
import {LoadingPanel} from '../LoadingPanel';
import {ProcessedPanel} from '../ProcessedPanel';
import {UploadingVideoButton} from './UploadVideoButton';
import {IVideoPanel} from '../../store/videoPanel/videoPanelReducer';
import {VideoContainer } from '../VideoContainer';

export function UploadingPage() {
  const processedVideoData = useSelector<IInitialState, IProcessedVideoData[]>(state => state.processedVideoData.processedVideoData);
  const videoPanelIsSwitched = useSelector<IInitialState, boolean>(state => state.videoPanelIsSwitched.videoPanelIsSwitched);
  const panelIsSwitched = useSelector<IInitialState, boolean>(state => state.panelIsSwitched.panelIsSwitched);
  const videoPanel = useSelector<IInitialState, IVideoPanel>(state => state.videoPanel.videoPanel);
  const uploadedVideos = useUploadedVideos();

  return (
    <div className={styles.container}>
      <div className={styles.wrapper}>
        <div className={styles.panel}>
          {uploadedVideos.length !== 0
            ? !panelIsSwitched
                ? <>
                    <LoadingPanel uploadedVideos={uploadedVideos} />
                    <UploadingText />
                  </>
                : !videoPanelIsSwitched
                    ? <>
                        <ProcessedPanel processedVideoData={processedVideoData}  />
                        <UploadingText />
                      </>
                    : <VideoContainer videoPanel={videoPanel} processedVideoData={processedVideoData} />
            : <UploadingVideoButton />
          }
        </div>
      </div>
    </div>
  );
}
