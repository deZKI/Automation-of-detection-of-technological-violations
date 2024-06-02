import { AnyAction, ActionCreator } from "redux";
import { ThunkDispatch } from "redux-thunk";
import { IInitialState } from "../reducer";
import { IUploadedVideo } from "../../hooks/useUploadedVideos";
import axios from 'axios';

export const SET_UPLOADED_VIDEO = 'SET_UPLOADED_VIDEO';

export type SetUploadedVideoAction = {
  type: typeof SET_UPLOADED_VIDEO;
  uploadedVideos: IUploadedVideo[];
}

export const setUploadedVideo: ActionCreator<SetUploadedVideoAction> = (uploadedVideos) => ({
  type: SET_UPLOADED_VIDEO,
  uploadedVideos
})

export const setUploadedVideoAsync = () => async (dispatch: ThunkDispatch<IInitialState, void, AnyAction>) => {
  axios.get('http://95.163.223.21/api/videos/')
    .then((res) => {
      const uploadedVideos: IUploadedVideo[] = res.data;
      dispatch(setUploadedVideo(uploadedVideos));
    })
    .catch((error) => {
      console.log(error);
    })
}
