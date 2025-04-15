import { useCallback, useEffect, useState } from "react";
import { useSocket } from "../../../contexts/socket/SocketContext";
import { Button } from "../../../contexts/socket/interfaces";
import ChatButton from "./ChatButton";
import "./ChatButtonBlock.css";

export function ChatButtonBlock({
  handleQuickReply,
  isWaitingForResponse,
}: {
  handleQuickReply: (text: string) => void;
  isWaitingForResponse: boolean;
}) {
  const [chatButtons, setChatButtons] = useState<JSX.Element[]>([]);
  const { onOptions, quickReply } = useSocket();

  const handleButtonClick = useCallback(
    (button: Button) => {
      quickReply(button);
      setChatButtons([]);
      handleQuickReply(button.text);
    },
    [quickReply, handleQuickReply]
  );

  useEffect(() => {
    onOptions((options: Button[]) => {
      const buttons = options.map((option, index) => (
        <ChatButton key={index} button={option} onClick={handleButtonClick} />
      ));
      setChatButtons(buttons);
    });
  }, [onOptions, handleButtonClick]);

  return (
    <div className="chat-button-group">
      <div className="d-flex flex-wrap justify-content-center gap-3">
        {!isWaitingForResponse && chatButtons}
      </div>
    </div>
  );
}
