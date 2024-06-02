import { initialState } from "../reducer";
import { SET_UPLOADED_VIDEO, SetUploadedVideoAction } from "./uploadedVideoActions";
import { IUploadedVideo } from "../../hooks/useUploadedVideos";

export interface IUploadedVideoState {
  uploadedVideo: IUploadedVideo[];
}

type UploadedVideoActions = SetUploadedVideoAction;

export const uploadedVideoReducer = (state = initialState.uploadedVideo, action: UploadedVideoActions): IUploadedVideoState => {
  switch (action.type) {
    case SET_UPLOADED_VIDEO:
      return {
        ...state,
        uploadedVideo: action.uploadedVideos
      }
    default:
      return state;
  }
}
