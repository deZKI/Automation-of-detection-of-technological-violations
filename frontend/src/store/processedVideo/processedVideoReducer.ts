import {initialState} from "../reducer";
import {SET_PROCESSED_VIDEO, SetProcessedVideoAction} from "./processedVideoActions";

export interface IProcessedVideoState {
  processedVideo: string;
}

type ProcessedVideoActions = SetProcessedVideoAction;

export const processedVideoReducer = (state = initialState.processedVideo, action: ProcessedVideoActions): IProcessedVideoState => {
  switch (action.type) {
    case SET_PROCESSED_VIDEO:
      return {
        ...state,
        processedVideo: action.processedVideo
      }
    default:
      return state;
  }
}

