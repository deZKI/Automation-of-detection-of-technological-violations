import {initialState} from "../reducer";
import {SET_VIDEO_PANEL_IS_SWITCHED, SetVideoPanelIsSwitchedAction} from "./videoPanelIsSwitchedActions";

export interface IVideoPanelIsSwitchedState {
  videoPanelIsSwitched: any;
}

type VideoPanelIsSwitchedActions = SetVideoPanelIsSwitchedAction;

export const videoPanelIsSwitchedReducer = (state = initialState.videoPanelIsSwitched, action: VideoPanelIsSwitchedActions): IVideoPanelIsSwitchedState => {
  switch (action.type) {
    case SET_VIDEO_PANEL_IS_SWITCHED:
      return {
        ...state,
        videoPanelIsSwitched: action.videoPanelIsSwitched
      }
    default:
      return state;
  }
}

