import {ActionCreator} from "redux";

export const SET_VIDEO_PANEL_IS_SWITCHED = 'SET_VIDEO_PANEL_IS_SWITCHED';

export type SetVideoPanelIsSwitchedAction = {
  type: typeof SET_VIDEO_PANEL_IS_SWITCHED;
  videoPanelIsSwitched: boolean;
}

export const setVideoPanelIsSwitched: ActionCreator<SetVideoPanelIsSwitchedAction> = (videoPanelIsSwitched) => ({
  type: SET_VIDEO_PANEL_IS_SWITCHED,
  videoPanelIsSwitched
})




