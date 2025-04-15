export type Settings = {
  style?: ChatMessageStyle;
};

export type ChatMessageStyle = {
  name?: string;
  showStyleSwitch?: boolean;
};

export type Query = {
  mode?: string;
  token?: string;
};

export type EventHandler = (event?: any) => void;
