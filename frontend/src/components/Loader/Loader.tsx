import React from 'react';
import styles from './loader.module.css';

export enum ESpinners {
  gray = 'gray',
  orange = 'orange'
}

interface ISpinnersProps {
  color: ESpinners;
}

export function Loader({ color }: ISpinnersProps) {
  return (
    <span className={styles.icon_loading}>
      <img className={styles.icon_loading_gif} src={`../../assets/images/${color}_spinner.gif`} alt="Лоудер" />
    </span>
  )
}
