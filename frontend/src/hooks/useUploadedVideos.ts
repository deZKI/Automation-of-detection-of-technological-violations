import { useEffect } from 'react';
import { useDispatch, useSelector } from "react-redux";
import { setUploadedVideoAsync } from '../store/uploadedVideo/uploadedVideoActions';
import { IInitialState } from "../store/reducer";
import { ThunkDispatch } from "redux-thunk";
import { AnyAction } from "redux";

export interface IUploadedVideo {
  id: number;
  video: string;
  title: string;
}

export function useUploadedVideos() {
  const uploadedVideos = useSelector<IInitialState, IUploadedVideo[]>(state => state.uploadedVideo.uploadedVideo);
  const dispatch = useDispatch<ThunkDispatch<IInitialState, void, AnyAction>>();

  useEffect(() => {
    dispatch(setUploadedVideoAsync())
  }, [dispatch]);

  return uploadedVideos;
}
