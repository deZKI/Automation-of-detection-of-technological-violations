import React from 'react';
import styles from './uploadingtext.module.css';

export function UploadingText() {
  return (
    <div className={styles.info}>
      <span className={styles.info__neuro}>нейро</span>
      <span className={styles.info__desc}>готово вам помочь!</span>
    </div>
  );
}
