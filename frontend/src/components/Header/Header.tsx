import React from 'react';
import styles from './header.module.css';
import LogoImage from '../../assets/images/logo.svg';

export function Header() {
  return (
    <header className={styles.container}>
      <div className={styles.wrapper}>
        <a className={styles.logo} href="/">
          <img className={styles.logo__image} src={LogoImage} alt="Логотип" />
        </a>
        <span className={styles.desc}>нейро</span>
      </div>
    </header>
  );
}
