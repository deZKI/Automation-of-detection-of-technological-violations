import React from 'react';
import styles from './uploadingpage.module.css';
import {useSelector} from "react-redux";
import {IInitialState} from '../../store/reducer';
import {LoadingPanel} from '../LoadingPanel';
import {StartProcessingButton} from './StartProcessingButton';
import {UploadingVideoButton} from './UploadVideoButton';
import {ESpinners, Loader} from '../Loader';

export function UploadingPage() {
  const uploadingPageLoader = useSelector<IInitialState, boolean>(state => state.uploadingPageLoader.uploadingPageLoader);
  const uploadedVideo = useSelector<IInitialState, any>(state => state.uploadedVideo.uploadedVideo);

  return (
    <div className={styles.container}>
      <div className={styles.wrapper}>
        <div className={styles.panel}>
          {!uploadingPageLoader
            ? <>
                {uploadedVideo.length !== 0
                  ? <>
                      <LoadingPanel />
                      <StartProcessingButton /> 
                    </>
                  : <UploadingVideoButton />
                }
              </>
            : <Loader color={ESpinners.orange} />
          }
        </div>
      </div>
    </div>
  );
}
