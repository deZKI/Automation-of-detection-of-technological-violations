import {ActionCreator} from "redux";
import {IVideoPanel} from "./videoPanelReducer";

export const SET_VIDEO_PANEL = 'SET_VIDEO_PANEL';

export type SetVideoPanelAction = {
  type: typeof SET_VIDEO_PANEL;
  videoPanel: IVideoPanel;
}

export const setVideoPanel: ActionCreator<SetVideoPanelAction> = (videoPanel) => ({
  type: SET_VIDEO_PANEL,
  videoPanel
})
