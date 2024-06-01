import {ActionCreator} from "redux";

export const SET_UPLOADED_VIDEO = 'SET_UPLOADED_VIDEO';

export type SetUploadedVideoAction = {
  type: typeof SET_UPLOADED_VIDEO;
  uploadedVideo: string;
}

export const setUploadedVideo: ActionCreator<SetUploadedVideoAction> = (uploadedVideo) => ({
  type: SET_UPLOADED_VIDEO,
  uploadedVideo
})

