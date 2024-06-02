import React from 'react';
import styles from './timestamps.module.css';

export function TimestampsPanel() {
  return (
    <div className={styles.container}>
      <ul className={styles.list}>
        <li className={styles.item}></li>
      </ul>
    </div>
  );
}
