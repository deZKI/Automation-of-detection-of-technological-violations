import {IProcessedVideoData} from "../store/processedVideoData/processedVideoDataReducer";

export interface ITimestamp {
  id: number;
  proceed_video: number;
  prediction: string;
  time_in_seconds: number;
}

export interface ICombinedObject {
  id: number;
  title: string;
  original_video: number;
  version: number;
  video: string;
  excel_file: string;
  pdf_file: string;
  timestamps: ITimestamp[];
}

export function combineObjects(processedVideoData: IProcessedVideoData, timestamps: ITimestamp[]): ICombinedObject {
  return {
    ...processedVideoData,
    timestamps: timestamps
  };
}