import React from 'react';
import styles from './loadinglist.module.css';
import {useDispatch, useSelector} from 'react-redux'; 
import axios from "axios";
import {IInitialState} from '../../../store/reducer';
import {setPanelIsSwitched} from '../../../store/panelIsSwitched/panelIsSwitchedActions';
import {IProcessedVideoData} from '../../../store/processedVideoData/processedVideoDataReducer';
import {setProcessedVideoData} from '../../../store/processedVideoData/processedVideoDataActions';
import {IUploadedVideo} from '../../../hooks/useUploadedVideos';

interface ILoadingListProps {
  uploadedVideos: IUploadedVideo[];
}

export function LoadingList({ uploadedVideos }: ILoadingListProps) {
  const panelIsSwitched = useSelector<IInitialState, boolean>(state => state.panelIsSwitched.panelIsSwitched);
  const dispatch = useDispatch();

  function handleClick(e: React.MouseEvent<HTMLElement>) {
    const buttonID = e.currentTarget.id;

    dispatch(setPanelIsSwitched(!panelIsSwitched));

    axios.get(`http://95.163.223.21/api/proceed-videos/${buttonID}/`)
    .then((res) => {
      const processedVideoData: IProcessedVideoData[] = res.data;
      dispatch(setProcessedVideoData(processedVideoData));
    })
    .catch((error) => {
      console.log(error);
    })
  }

  return (
    <ul className={styles.list}>
      {uploadedVideos.map((video) =>
        <li className={styles.item}>
          <button id={`${video.id}`} className={styles.button} onClick={handleClick}>
            {video.title}
          </button>
        </li>
      )}
    </ul>
  );
}
