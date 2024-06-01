import {ActionCreator} from "redux";

export const SET_PROCESSED_VIDEO = 'SET_PROCESSED_VIDEO';

export type SetProcessedVideoAction = {
  type: typeof SET_PROCESSED_VIDEO;
  processedVideo: string;
}

export const setProcessedVideo: ActionCreator<SetProcessedVideoAction> = (processedVideo) => ({
  type: SET_PROCESSED_VIDEO,
  processedVideo
})
