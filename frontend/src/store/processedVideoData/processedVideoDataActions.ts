import {ActionCreator} from "redux";
import {IProcessedVideoData} from "./processedVideoDataReducer";

export const SET_PROCESSED_VIDEO_DATA = 'SET_PROCESSED_VIDEO_DATA';

export type SetProcessedVideoDataAction = {
  type: typeof SET_PROCESSED_VIDEO_DATA;
  processedVideoData: IProcessedVideoData[];
}

export const setProcessedVideoData: ActionCreator<SetProcessedVideoDataAction> = (processedVideoData) => ({
  type: SET_PROCESSED_VIDEO_DATA,
  processedVideoData
})
