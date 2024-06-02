import React from 'react';
import styles from './processedpanelbutton.module.css';
import {useDispatch, useSelector} from 'react-redux';
import {IInitialState} from '../../../store/reducer';
import {setPanelIsSwitched} from '../../../store/panelIsSwitched/panelIsSwitchedActions';

export function ProcessedPanelButton() {
  const panelIsSwitched = useSelector<IInitialState, boolean>(state => state.panelIsSwitched.panelIsSwitched);
  const dispatch = useDispatch();

  function handleClick() {
    dispatch(setPanelIsSwitched(!panelIsSwitched));
  }

  return (
    <button className={styles.button} onClick={handleClick}>
    <span className={styles.desc}>Загруженные видео</span>
    <span className={styles.icon}>
      <svg xmlns="http://www.w3.org/2000/svg" xmlnsXlink="http://www.w3.org/1999/xlink" fill="#DA4216" height="16px" width="16px" version="1.1" id="Layer_1" viewBox="0 0 330 330" xmlSpace="preserve">
        <path id="XMLID_222_" d="M250.606,154.389l-150-149.996c-5.857-5.858-15.355-5.858-21.213,0.001  c-5.857,5.858-5.857,15.355,0.001,21.213l139.393,139.39L79.393,304.394c-5.857,5.858-5.857,15.355,0.001,21.213  C82.322,328.536,86.161,330,90,330s7.678-1.464,10.607-4.394l149.999-150.004c2.814-2.813,4.394-6.628,4.394-10.606  C255,161.018,253.42,157.202,250.606,154.389z"/>
      </svg>
    </span>
  </button>
  );
}
