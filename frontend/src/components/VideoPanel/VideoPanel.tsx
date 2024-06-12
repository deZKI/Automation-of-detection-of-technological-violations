import React from 'react';
import styles from './videopanel.module.css';
import ReactPlayer from 'react-player';
import {IVideoPanel} from '../../store/videoPanel/videoPanelReducer';

interface IVideoPanelProps {
  videoPanel: IVideoPanel;
  playerRef: React.RefObject<ReactPlayer>;
}

export function VideoPanel({ videoPanel, playerRef }: IVideoPanelProps) {
  return (
    <div className={styles.container}>
      <ReactPlayer ref={playerRef} url={videoPanel.video} controls />
      <div className={styles.downloads}>
        <a className={styles.button} href={`http://95.163.223.21${videoPanel.pdf_file}`} target="_blank" download>Выгрузить PDF</a>
        <a className={styles.button} href={`http://95.163.223.21${videoPanel.excel_file}`} download>Выгрузить XLSX</a>
      </div>
    </div>
  );
}
