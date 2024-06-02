import {IProcessedVideoState, processedVideoReducer} from "./processedVideo/processedVideoReducer";
import {SET_PROCESSED_VIDEO, SetProcessedVideoAction} from "./processedVideo/processedVideoActions";
import {IUploadedVideoState, uploadedVideoReducer} from "./uploadedVideo/uploadedVideoReducer";
import {SET_UPLOADED_VIDEO, SetUploadedVideoAction} from "./uploadedVideo/uploadedVideoActions";
import {IUploadingPageLoaderState, uploadingPageLoaderReducer } from "./uploadingPageLoader/uploadingPageLoaderReducer";
import {SET_UPLOADING_PAGE_LOADER, SetUploadingPageLoaderAction} from "./uploadingPageLoader/uploadingPageLoaderActions";
import {IPanelIsSwitchedState, panelIsSwitchedReducer} from "./panelIsSwitched/panelIsSwitchedReducer";
import {SET_PANEL_IS_SWITCHED, SetPanelIsSwitchedAction} from "./panelIsSwitched/panelIsSwitchedActions";
import {IProcessedVideoDataState, processedVideoDataReducer} from "./processedVideoData/processedVideoDataReducer";
import {SET_PROCESSED_VIDEO_DATA, SetProcessedVideoDataAction} from "./processedVideoData/processedVideoDataActions";
import {IVideoPanelIsSwitchedState, videoPanelIsSwitchedReducer} from "./videoPanelIsSwitched/videoPanelIsSwitchedReducer";
import {SET_VIDEO_PANEL_IS_SWITCHED, SetVideoPanelIsSwitchedAction} from "./videoPanelIsSwitched/videoPanelIsSwitchedActions";
import {IVideoPanelState, videoPanelReducer} from "./videoPanel/videoPanelReducer";
import {SET_VIDEO_PANEL, SetVideoPanelAction} from "./videoPanel/videoPanelActions";

export interface IInitialState {
  processedVideo: IProcessedVideoState;
  uploadedVideo: IUploadedVideoState;
  processedVideoData: IProcessedVideoDataState;
  uploadingPageLoader: IUploadingPageLoaderState;
  panelIsSwitched: IPanelIsSwitchedState;
  videoPanelIsSwitched: IVideoPanelIsSwitchedState;
  videoPanel: IVideoPanelState;
}

export const initialState: IInitialState = {
  processedVideo: {
    processedVideo: ""
  },
  uploadedVideo: {
    uploadedVideo: []
  },
  processedVideoData: {
    processedVideoData: []
  },
  uploadingPageLoader: {
    uploadingPageLoader: false
  },
  panelIsSwitched: {
    panelIsSwitched: false
  },
  videoPanelIsSwitched: {
    videoPanelIsSwitched: false
  },
  videoPanel: {
    videoPanel: {}
  }
}

type Actions = SetProcessedVideoAction 
  | SetUploadedVideoAction 
  | SetProcessedVideoDataAction
  | SetUploadingPageLoaderAction
  | SetPanelIsSwitchedAction
  | SetVideoPanelIsSwitchedAction
  | SetVideoPanelAction

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
    case SET_PROCESSED_VIDEO_DATA:
      return {
        ...state,
        processedVideoData: processedVideoDataReducer(state.processedVideoData, action)
      }
    case SET_UPLOADING_PAGE_LOADER:
      return {
        ...state,
        uploadingPageLoader: uploadingPageLoaderReducer(state.uploadingPageLoader, action)
      }
    case SET_PANEL_IS_SWITCHED:
      return {
        ...state,
        panelIsSwitched: panelIsSwitchedReducer(state.panelIsSwitched, action)
      }
    case SET_VIDEO_PANEL_IS_SWITCHED:
      return {
        ...state,
        videoPanelIsSwitched: videoPanelIsSwitchedReducer(state.videoPanelIsSwitched, action)
      }
    case SET_VIDEO_PANEL:
        return {
          ...state,
          videoPanel: videoPanelReducer(state.videoPanel, action)
        }
    default:
      return state;
  }
}
