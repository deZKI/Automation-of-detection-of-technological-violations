import React from 'react';
import styles from './loadinglist.module.css';
import {TickIcon} from '../../Icons/TickIcon';
import { ESpinners, Loader } from '../../Loader';

export function LoadingList() {
  return (
    <ul className={styles.list}>
      <li className={styles.item}>
        <span className={`${styles.desc} ${styles.desc_success}`}>file-video.mp4;lskdafjd;lfkj</span>
        <span className={styles.icon_success}><TickIcon /></span>
      </li>
      <li className={styles.item}>
        <span className={styles.desc}>file-video.mp4</span>
        <Loader color={ESpinners.gray} />
      </li>
    </ul>
  );
}
