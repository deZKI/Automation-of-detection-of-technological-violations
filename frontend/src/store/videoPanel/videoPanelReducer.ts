import {initialState } from "../reducer";
import {SET_VIDEO_PANEL, SetVideoPanelAction} from "./videoPanelActions";

export interface IVideoPanel {
  id: number;
  video: string;
  excel_file: string;
  pdf_file: string;
}

export interface IVideoPanelState {
  videoPanel: any;
}

type VideoPanelActions = SetVideoPanelAction;

export const videoPanelReducer = (state = initialState.videoPanel, action: VideoPanelActions): IVideoPanelState => {
  switch (action.type) {
    case SET_VIDEO_PANEL:
      return {
        ...state,
        videoPanel: action.videoPanel
      }
    default:
      return state;
  }
}

