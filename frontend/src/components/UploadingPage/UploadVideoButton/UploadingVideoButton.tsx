import React from 'react';
import styles from './uploadingvideobutton.module.css';
import {useDispatch} from "react-redux";
import {setUploadedVideo} from '../../../store/uploadedVideo/uploadedVideoActions';

export function UploadingVideoButton() {
  const dispatch = useDispatch();
  
  function handleChange(e: any) {
    const file = e.target.files[0];
    const fileReader = new FileReader();

    fileReader.readAsDataURL(file);
    fileReader.onload = () => {
      dispatch(setUploadedVideo(fileReader.result));
    };
  }
  
  return (
    <label className={styles.button} htmlFor="load_video">
      <input id="load_video" type="file" accept="video/*" onChange={handleChange} />
      <span className={styles.desc}>Загрузить видео</span>
    </label>
  );
}
