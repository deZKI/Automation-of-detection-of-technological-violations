import {IProcessedVideoState, processedVideoReducer} from "./processedVideo/processedVideoReducer";
import {SET_PROCESSED_VIDEO, SetProcessedVideoAction} from "./processedVideo/processedVideoActions";
import {IUploadedVideoState, uploadedVideoReducer} from "./uploadedVideo/uploadedVideoReducer";
import {SET_UPLOADED_VIDEO, SetUploadedVideoAction} from "./uploadedVideo/uploadedVideoActions";
import {IUploadingPageLoaderState, uploadingPageLoaderReducer } from "./uploadingPageLoader/uploadingPageLoaderReducer";
import {SET_UPLOADING_PAGE_LOADER, SetUploadingPageLoaderAction} from "./uploadingPageLoader/uploadingPageLoaderActions";

export interface IInitialState {
  processedVideo: IProcessedVideoState;
  uploadedVideo: IUploadedVideoState;
  uploadingPageLoader: IUploadingPageLoaderState;
}

export const initialState: IInitialState = {
  processedVideo: {
    processedVideo: ""
  },
  uploadedVideo: {
    uploadedVideo: ""
  },
  uploadingPageLoader: {
    uploadingPageLoader: false
  }
}

type Actions = SetProcessedVideoAction | SetUploadedVideoAction | SetUploadingPageLoaderAction

export const rootReducer = (state = initialState, action: Actions): IInitialState => {
  switch (action.type) {
    case SET_PROCESSED_VIDEO:
      return {
        ...state,
        processedVideo: processedVideoReducer(state.processedVideo, action)
      }
    case SET_UPLOADED_VIDEO:
      return {
        ...state,
        uploadedVideo: uploadedVideoReducer(state.uploadedVideo, action)
      }
    case SET_UPLOADING_PAGE_LOADER:
      return {
        ...state,
        uploadingPageLoader: uploadingPageLoaderReducer(state.uploadingPageLoader, action)
      }
    default:
      return state;
  }
}
