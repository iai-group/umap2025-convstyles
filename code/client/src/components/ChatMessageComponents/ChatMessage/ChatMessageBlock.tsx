import { Message } from "../../ChatBox/ChatBox";
import { UserChatMessage } from "./UserChatMessage";
import { SystemChatMessage } from "./SystemChatMessage";
import { useEffect } from "react";

export const ChatMessageBlock = ({ messages }: { messages: Message[] }) => {
  // const lastSystemIndex = messages.map((m) => m.type).lastIndexOf("system");

  // useEffect(() => {
  //   console.log(messages);
  // });

  return (
    <div>
      {messages.map((msg, index) => {
        if (msg.type === "user") {
          return (
            <UserChatMessage key={index} message={msg.message as string} />
          );
        } else {
          return (
            <SystemChatMessage
              key={index}
              message={
                typeof msg.message === "string" ? (
                  <div
                    dangerouslySetInnerHTML={{
                      __html: msg.message,
                    }}
                  ></div>
                ) : (
                  <>msg.message</>
                )
              }
            />
          );
        }
      })}
    </div>
  );
};
