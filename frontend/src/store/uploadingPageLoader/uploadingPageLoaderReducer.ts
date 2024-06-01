import {initialState} from "../reducer";
import {SET_UPLOADING_PAGE_LOADER, SetUploadingPageLoaderAction} from "./uploadingPageLoaderActions";

export interface IUploadingPageLoaderState {
  uploadingPageLoader: boolean;
}

type UploadingPageLoaderActions = SetUploadingPageLoaderAction;

export const uploadingPageLoaderReducer = (state = initialState.uploadingPageLoader, action: UploadingPageLoaderActions): IUploadingPageLoaderState => {
  switch (action.type) {
    case SET_UPLOADING_PAGE_LOADER:
      return {
        ...state,
        uploadingPageLoader: action.uploadingPageLoader
      }
    default:
      return state;
  }
}



