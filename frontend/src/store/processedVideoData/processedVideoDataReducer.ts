import {initialState} from "../reducer";
import {SET_PROCESSED_VIDEO_DATA, SetProcessedVideoDataAction} from "./processedVideoDataActions";

export interface IProcessedVideoData {
  id: number;
  title: string;
  original_video: number;
  version: number;
  video: string;
  excel_file: string;
  pdf_file: string;
}

export interface IProcessedVideoDataState {
  processedVideoData: IProcessedVideoData[];
}

type ProcessedVideoDataActions = SetProcessedVideoDataAction;

export const processedVideoDataReducer = (state = initialState.processedVideoData, action: ProcessedVideoDataActions): IProcessedVideoDataState => {
  switch (action.type) {
    case SET_PROCESSED_VIDEO_DATA:
      return {
        ...state,
        processedVideoData: action.processedVideoData
      }
    default:
      return state;
  }
}

