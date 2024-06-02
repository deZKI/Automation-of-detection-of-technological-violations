import React from 'react';
import styles from './videopanel.module.css';
import ReactPlayer from 'react-player';
import useDownloader from 'react-use-downloader';
import {useSelector} from 'react-redux';
import {IVideoPanel} from '../../store/videoPanel/videoPanelReducer';
import {IInitialState} from '../../store/reducer';

export function VideoPanel() {
  const videoPanel = useSelector<IInitialState, IVideoPanel>(state => state.videoPanel.videoPanel);
  const {download} = useDownloader();

  function handleClickPDF() {
    download(videoPanel.pdf_file, 'детектирование нарушений');
  }

  function handleClickXLSX() {
    download(videoPanel.excel_file, 'детектирование нарушений');
  }

  return (
    <div className={styles.container}>
      <ReactPlayer url={videoPanel.video} controls />
      <div className={styles.downloads}>
        <button id="download_button-pdf" className={styles.button} onClick={handleClickPDF}>Выгрузить PDF</button>
        <button id="download_button-xlsx" className={styles.button} onClick={handleClickXLSX}>Выгрузить XLSX</button>
      </div>
    </div>
  )
}
