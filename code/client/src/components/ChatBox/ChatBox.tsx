import "./ChatBox.css";

import React, {
  useState,
  useEffect,
  useRef,
  useCallback,
  useContext,
} from "react";
import { useSocket } from "../../contexts/socket/SocketContext";
import { UserContext } from "../../contexts/UserContext";
import {
  MDBCard,
  MDBCardHeader,
  MDBCardBody,
  MDBIcon,
  MDBCardFooter,
  MDBSwitch,
} from "mdb-react-ui-kit";
import { Article, SystemMessage } from "../../contexts/socket/interfaces";
import { ConfigContext } from "../../contexts/ConfigContext";
import { ChatButtonBlock } from "../ChatMessageComponents/ChatButton/ChatButtonBlock";
import { ChatMessageBlock } from "../ChatMessageComponents/ChatMessage/ChatMessageBlock";
import { WaitingSystemChatMessage } from "../ChatMessageComponents/ChatMessage/WaitingSystemChatMessage";
import { useGlobalState } from "../../contexts/GlobalStateContext";
import { log } from "console";

export enum StyleOption {
  DEFAULT = "default",
  CONSIDERATE = "considerate",
  INVOLVED = "involved",
}

type Keystroke = {
  key: string;
  timestamp: string;
};

export interface Message {
  type: "user" | "system";
  message: string;
}

export function ChatBox({
  style,
  showStyleSwitch = false,
}: {
  style: StyleOption;
  showStyleSwitch?: boolean;
}) {
  const { config } = useContext(ConfigContext);
  const { user } = useContext(UserContext);

  const {
    // settings,
    startConversation,
    sendMessage,
    onMessage,
    onEOT,
    // onRestart,
    // giveFeedback,
    setStyle,
    logEvent,
  } = useSocket();
  const [conversationStarted, setConversationStarted] = useState(false);
  const [isWaitingForResponse, setIsWaitingForResponse] = useState(true);
  const [isWaitingForResponseStart, setIsWaitingForResponseStart] =
    useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState<string>("");
  const [keystrokes, setKeystrokes] = useState<Keystroke[]>([]);
  const [selectedStyle, setSelectedStyle] = useState<string>();
  const { globalState, setGlobalState } = useGlobalState();

  // const [showStyleSwitch, setShowStyleSwitch] = useState<boolean>();
  const inputRef = useRef<HTMLInputElement>(null);

  // useEffect(() => {
  //   if (settings) {
  //     setSelectedStyle(settings?.style?.name);
  //     setShowStyleSwitch(settings?.style?.showStyleSwitch);
  //   }
  // }, [settings]);

  const setChatIsBusy = useCallback(
    (state: boolean) => {
      setGlobalState((prevState) => ({
        ...prevState,
        chat_box: {
          ...prevState.chat_box,
          chatIsBusy: state,
        },
      }));
      setIsWaitingForResponse(state);
      if (state) {
        setIsWaitingForResponseStart(true);
      }
    },
    [setGlobalState]
  );

  const explainRecommendation = useCallback(
    (article: Article) => {
      setChatIsBusy(true);
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          type: "user",
          message: `Explain recommendation for the article: ${article.title}`,
        },
      ]);
    },
    [setMessages, setChatIsBusy]
  );

  useEffect(() => {
    setGlobalState((prevGlobalState) => ({
      ...prevGlobalState,
      chat_box: {
        ...prevGlobalState.chat_box,
        handleExplainRecommendation: explainRecommendation,
      },
    }));
  }, [setGlobalState, explainRecommendation]);

  useEffect(() => {
    setSelectedStyle((prevStyle) => {
      if (style !== prevStyle) setStyle(style);
      return style;
    });
  }, [style, setStyle]);

  useEffect(() => {
    if (selectedStyle && !conversationStarted) {
      setChatIsBusy(true);
      startConversation();
      setConversationStarted(true);
      logEvent({
        event: "Start conversation",
      });
    }
  }, [selectedStyle, startConversation, conversationStarted, setChatIsBusy]);

  useEffect(() => {
    if (isWaitingForResponseStart) {
      console.log("Waiting for response start");
    }
  }, [isWaitingForResponseStart]);

  const handleKeystrokeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = e.target;
    setInputValue(value);
    setKeystrokes([
      ...keystrokes,
      { key: value[value.length - 1], timestamp: new Date().toISOString() },
    ]);
  };

  useEffect(() => {
    if (inputRef.current && !isWaitingForResponse) {
      inputRef.current.focus();
    }
  }, [isWaitingForResponse]);

  const handleInput = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (inputValue.trim() === "") return;
    setChatIsBusy(true);
    setMessages((prevMessages) => [
      ...prevMessages,
      { type: "user", message: inputValue },
    ]);
    sendMessage({ message: inputValue, metadata: { keystrokes: keystrokes } });
    setInputValue("");
    setKeystrokes([]);
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  const handleQuickReply = useCallback(
    (text: string) => {
      setChatIsBusy(true);
      setMessages((prevMessages) => [
        ...prevMessages,
        { type: "user", message: text },
      ]);
    },
    [setMessages, setChatIsBusy]
  );

  useEffect(() => {
    onMessage((message: SystemMessage) => {
      setMessages((prevMessages) => {
        if (message.info === "NEW") {
          setIsWaitingForResponseStart(false);
          return [...prevMessages, { type: "system", message: message.text }];
        }

        const lastMessageIndex = prevMessages.length - 1;
        const lastMessage = prevMessages[lastMessageIndex];

        if (!lastMessage) return prevMessages;

        // Create a new message with appended text
        const updatedMessage = {
          ...lastMessage,
          message: lastMessage.message + message.text,
        };
        const updatedMessages = [...prevMessages];
        updatedMessages[lastMessageIndex] = updatedMessage;

        return updatedMessages;
      });
    });
  }, [onMessage]);

  useEffect(() => {
    onEOT(() => {
      setChatIsBusy(false);
    });
  }, [onEOT, setChatIsBusy]);

  const handleStyleChange = () => {
    const style =
      selectedStyle === StyleOption.INVOLVED
        ? StyleOption.CONSIDERATE
        : StyleOption.INVOLVED;
    setSelectedStyle(style);
    setStyle(style);
    logEvent({
      event: "Change style",
      metadata: { style: style },
    });
  };

  return (
    <div className="chat-widget-content">
      <MDBCard
        id="chatBox"
        className="chat-widget-card"
        style={{ borderRadius: "15px" }}
      >
        <MDBCardHeader
          className="d-flex justify-content-between align-items-center p-3 bg-info text-white border-bottom-0"
          style={{
            borderTopLeftRadius: "15px",
            borderTopRightRadius: "15px",
          }}
        >
          <p className="mb-0 fw-bold">{config.name}</p>
          <div className="mb-0 d-flex align-items-center">
            <p className="mb-0 fw-bold">{user?.username}</p>
            <p className="mb-0 fw-bold mx-2">Considerate </p>{" "}
            <MDBSwitch
              checked={selectedStyle === StyleOption.INVOLVED}
              onChange={handleStyleChange}
              disabled={!showStyleSwitch || isWaitingForResponse}
              style={
                !showStyleSwitch || isWaitingForResponse ? { opacity: 0.3 } : {}
              }
            />
            <p className="mb-0 fw-bold mx-2">Involved </p>
            {/* <div className="mx-2">
              <button
                className={`btn ${
                  selectedStyle === "considerate" ? "btn-primary" : "btn-light"
                }`}
                onClick={() => handleStyleChange("considerate")}
              >
                Considerate
              </button>
              <button
                className={`btn ${
                  selectedStyle === "default" ? "btn-primary" : "btn-light"
                }`}
                onClick={() => handleStyleChange("default")}
              >
                Default
              </button>
              <button
                className={`btn ${
                  selectedStyle === "involved" ? "btn-primary" : "btn-light"
                }`}
                onClick={() => handleStyleChange("involved")}
              >
                Involved
              </button>
            </div> */}
          </div>
        </MDBCardHeader>

        <MDBCardBody>
          <div className="card-body-messages">
            <ChatMessageBlock messages={messages} />
            {isWaitingForResponseStart && <WaitingSystemChatMessage />}
            <ChatButtonBlock
              handleQuickReply={handleQuickReply}
              isWaitingForResponse={isWaitingForResponse}
            />
          </div>
        </MDBCardBody>
        <MDBCardFooter className="text-muted d-flex justify-content-start align-items-center p-2">
          <form className="d-flex flex-grow-1" onSubmit={handleInput}>
            <input
              type="text"
              className="form-control form-control-lg"
              id="ChatInput"
              onChange={handleKeystrokeChange}
              placeholder="Type message"
              ref={inputRef}
              disabled={isWaitingForResponse}
              style={{ backgroundColor: isWaitingForResponse ? "DDD" : "000" }}
            ></input>
            <button type="submit" className="btn btn-link text-muted">
              <MDBIcon fas size="2x" icon="paper-plane" />
            </button>
          </form>
        </MDBCardFooter>
      </MDBCard>
    </div>
  );
}
