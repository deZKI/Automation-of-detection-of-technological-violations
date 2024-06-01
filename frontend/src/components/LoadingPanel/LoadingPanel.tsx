import React from 'react';
import styles from './loadingpanel.module.css';
import { LoadingList } from './LoadingList';
import { LoadingButton } from './LoadingButton';

export function LoadingPanel() {
  return (
    <div className={styles.container}>
      <LoadingList />
      <LoadingButton />
    </div>
  );
}
