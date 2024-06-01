import {ActionCreator} from "redux";

export const SET_UPLOADING_PAGE_LOADER = 'SET_UPLOADING_PAGE_LOADER';

export type SetUploadingPageLoaderAction = {
  type: typeof SET_UPLOADING_PAGE_LOADER;
  uploadingPageLoader: boolean;
}

export const setUploadingPageLoader: ActionCreator<SetUploadingPageLoaderAction> = (uploadingPageLoader) => ({
  type: SET_UPLOADING_PAGE_LOADER,
  uploadingPageLoader
})


