import React, { createContext, useContext, useState, ReactNode } from "react";
import { Article } from "./socket/interfaces";

type ChatBoxState = {
  handleExplainRecommendation?: (article: Article) => void;
  chatIsBusy: boolean;
};

type GlobalState = {
  chat_box: ChatBoxState;
};

type GlobalStateContextType = {
  globalState: GlobalState;
  setGlobalState: React.Dispatch<React.SetStateAction<GlobalState>>;
};

const GlobalStateContext = createContext<GlobalStateContextType | undefined>(
  undefined
);

type GlobalStateProviderProps = {
  children: ReactNode;
};

export const GlobalStateProvider: React.FC<GlobalStateProviderProps> = ({
  children,
}) => {
  const [globalState, setGlobalState] = useState<GlobalState>({
    chat_box: {
      chatIsBusy: false,
    },
  });

  return (
    <GlobalStateContext.Provider value={{ globalState, setGlobalState }}>
      {children}
    </GlobalStateContext.Provider>
  );
};

export const useGlobalState = () => {
  const context = useContext(GlobalStateContext);
  if (!context) {
    throw new Error("useGlobalState must be used within a GlobalStateProvider");
  }
  return context;
};
