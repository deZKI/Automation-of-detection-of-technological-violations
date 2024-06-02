import {ActionCreator} from "redux";

export const SET_PANEL_IS_SWITCHED = 'SET_PANEL_IS_SWITCHED';

export type SetPanelIsSwitchedAction = {
  type: typeof SET_PANEL_IS_SWITCHED;
  panelIsSwitched: boolean;
}

export const setPanelIsSwitched: ActionCreator<SetPanelIsSwitchedAction> = (panelIsSwitched) => ({
  type: SET_PANEL_IS_SWITCHED,
  panelIsSwitched
})



