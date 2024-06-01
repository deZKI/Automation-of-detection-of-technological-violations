import {initialState} from "../reducer";
import {SET_UPLOADED_VIDEO, SetUploadedVideoAction} from "./uploadedVideoActions";

export interface IUploadedVideoState {
  uploadedVideo: string;
}

type UploadedVideoActions = SetUploadedVideoAction;

export const uploadedVideoReducer = (state = initialState.uploadedVideo, action: UploadedVideoActions): IUploadedVideoState => {
  switch (action.type) {
    case SET_UPLOADED_VIDEO:
      return {
        ...state,
        uploadedVideo: action.uploadedVideo
      }
    default:
      return state;
  }
}


