import { SystemChatMessage } from "./SystemChatMessage";
import "./WaitingSystemChatMessage.css";

export const WaitingSystemChatMessage = (): JSX.Element => {
  return (
    <SystemChatMessage
      message={
        <div className="animated-text-container">
          <span className="dot">.</span>
          <span className="dot">.</span>
          <span className="dot">.</span>
        </div>
      }
    />
  );
};
