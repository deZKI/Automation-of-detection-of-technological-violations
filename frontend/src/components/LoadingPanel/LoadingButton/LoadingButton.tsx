import React from 'react';
import styles from './loadingbutton.module.css';
import axios from 'axios';

export function LoadingButton() {
  function handleChange(e: any) {
    const file = e.target.files[0];
    const formData = new FormData();
    
    formData.append('title', file.name);
    formData.append('video', file);

    axios.post('http://95.163.223.21/api/videos/', formData, {
      headers: {
        'accept': 'application/json',
        'Content-Type': 'multipart/form-data',
        'X-CSRFToken': '1tKCiJEvIMNUH08wdOYcaSUPVYNgi9iniObQAIOVhErFJ2uOv3LOz7YdDQoDOrlx',
      }
    })
    .catch((err) => {
      console.error(err);
    });
  }

  return (
    <label className={styles.button} htmlFor="loading_button">
      <input id="loading_button" type="file" accept="video/*" onChange={handleChange} />
      <span className={styles.desc}>Добавить видео</span>
    </label>
  );
}
