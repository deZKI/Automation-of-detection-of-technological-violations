import React from 'react';
import styles from './processedlist.module.css';
import {useDispatch} from 'react-redux';
import {IProcessedVideoData} from '../../../store/processedVideoData/processedVideoDataReducer';
import {setVideoPanelIsSwitched} from '../../../store/videoPanelIsSwitched/videoPanelIsSwitchedActions';
import {setVideoPanel} from '../../../store/videoPanel/videoPanelActions';

interface IProcessedListProps {
  processedVideoData: IProcessedVideoData[];
}

export function ProcessedList({ processedVideoData }: IProcessedListProps) {
  const dispatch = useDispatch();

  function handleClick(e: React.MouseEvent<HTMLElement>) {
    const buttonID = e.currentTarget.id;

    dispatch(setVideoPanelIsSwitched(true));
    
    processedVideoData.map((processedVideo) => {
      if (processedVideo.id === Number(buttonID)) {
        dispatch(setVideoPanel({
          id: processedVideo.id,
          title: processedVideo.title,
          video: `http://95.163.223.21${processedVideo.video}`,
          excel_file: processedVideo.excel_file,
          pdf_file: processedVideo.pdf_file
        }));
      }
    });
  }

  return (
    <ul className={styles.list}>
      {processedVideoData.map((video) =>
        <li className={styles.item}>
          <button id={`${video.id}`} className={styles.button} onClick={handleClick}>
            {video.title}
          </button>
        </li>
      )}
    </ul>
  );
}
