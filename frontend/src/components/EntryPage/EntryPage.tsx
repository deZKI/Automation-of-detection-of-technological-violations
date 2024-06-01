import React from 'react';
import styles from './entrypage.module.css';

export function EntryPage() {
  return (
    <div className={styles.container}>
      <div className={styles.wrapper}>
        <div className={styles.intro}>
          <div className={styles.intro__wrapper}>
            <h1 className={styles.intro__title}>РЖД</h1>
            <p className={styles.intro__desc}>Автоматизация выявления<br/>технологических нарушений</p>
            <a className={styles.intro__button} href="/load">Загрузить</a>
          </div>
        </div>
        <div className={styles.background}></div>
      </div>
    </div>
  );
}
