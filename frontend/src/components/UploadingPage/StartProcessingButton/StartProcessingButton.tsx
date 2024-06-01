import React from 'react';
import styles from './startprocessingbutton.module.css';
import axios from 'axios';
import {useDispatch, useSelector} from "react-redux";
import {IInitialState} from '../../../store/reducer';
import {setUploadingPageLoader} from '../../../store/uploadingPageLoader/uploadingPageLoaderActions';
import {setProcessedVideo} from '../../../store/processedVideo/processedVideoActions';

export function StartProcessingButton() {
  const uploadedVideo = useSelector<IInitialState, any>(state => state.uploadedVideo.uploadedVideo);
  const dispatch = useDispatch();

  function handleClick() {
    const formData = new FormData();
    formData.append('map', uploadedVideo, uploadedVideo.name);

    dispatch(setUploadingPageLoader(true));

    axios.post("http://localhost:8000/ai/", formData)
      .then((res) => {
        const data = res.data.file_path;

        dispatch(setUploadingPageLoader(false));
        dispatch(setProcessedVideo(data));
      })
      .catch((err) => {
        console.log(err.toString());
      })
  }

  return (
    <button className={styles.button} onClick={handleClick}>Начать обработку</button> 
  );
}
