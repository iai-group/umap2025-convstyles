import React, { createContext, useContext, ReactNode } from "react";
import useSocketConnection from "./socket_connector";

interface SocketProviderProps {
  children: ReactNode;
}

const SocketContext = createContext<ReturnType<
  typeof useSocketConnection
> | null>(null);

export const useSocket = () => {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error("useSocket must be used within a SocketProvider");
  }
  return context;
};

export const SocketProvider: React.FC<SocketProviderProps> = ({ children }) => {
  const socketMethods = useSocketConnection();

  return (
    <SocketContext.Provider value={socketMethods}>
      {children}
    </SocketContext.Provider>
  );
};
